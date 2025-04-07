#!/usr/bin/env python3
import os
import subprocess
import psutil
import time
import json
import logging
import re
import werkzeug
import secrets
import datetime
from urllib.parse import urlparse
from functools import wraps

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, abort
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "development_secret_key")

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize SQLAlchemy
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Initialize Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Load environment variables
load_dotenv()

# Import other modules after configuration
import config
from logger import logger
import email_utils
from models import User, RunningTool, ToolLog

# Track online users
online_users = {}

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def get_online_users_count():
    """Get count of online users in the last 5 minutes"""
    now = time.time()
    active_users = [u for u, t in online_users.items() if now - t < 300]
    return len(active_users)

@app.before_request
def update_last_seen():
    """Update the last seen time for the current user"""
    if current_user.is_authenticated:
        session.permanent = True
        app.permanent_session_lifetime = datetime.timedelta(days=7)
        current_user.last_login = datetime.datetime.utcnow()
        db.session.commit()
        online_users[current_user.id] = time.time()

def get_base_url():
    """Get the base URL of the application"""
    host = request.headers.get('Host', 'localhost:5000')
    scheme = request.headers.get('X-Forwarded-Proto', 'http')
    return f"{scheme}://{host}"

def is_bot_running(user_id=None, tool_id=None):
    """Check if bot process is running for a specific user or tool"""
    query = RunningTool.query.filter_by(status='running')
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    if tool_id:
        query = query.filter_by(id=tool_id)
    
    tools = query.all()
    
    for tool in tools:
        if tool.process_id:
            try:
                process = psutil.Process(tool.process_id)
                if process.is_running():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # Process doesn't exist anymore, update status
                tool.status = 'crashed'
                db.session.commit()
    
    return False

def format_uptime(seconds):
    """Format uptime in a human-readable format"""
    if seconds < 60:
        return f"{int(seconds)} seconds"
    elif seconds < 3600:
        return f"{int(seconds / 60)} minutes"
    else:
        return f"{int(seconds / 3600)} hours, {int((seconds % 3600) / 60)} minutes"

def get_bot_logs(tool_id, limit=10):
    """Get the logs for a specific bot"""
    return ToolLog.query.filter_by(tool_id=tool_id).order_by(ToolLog.timestamp.desc()).limit(limit).all()

def add_bot_log(tool_id, message, level='INFO'):
    """Add a log entry for a specific bot"""
    log = ToolLog(tool_id=tool_id, message=message, level=level)
    db.session.add(log)
    db.session.commit()
    return log

#########################
# Authentication Routes #
#########################

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        agree_tos = request.form.get('agree_tos')
        
        # Validate input
        error = None
        if not username or not email or not password or not agree_tos:
            error = "All fields are required, including accepting the Terms of Service"
        elif not re.match(r'^[a-zA-Z0-9_]+$', username):
            error = "Username can only contain letters, numbers, and underscores"
        elif User.query.filter_by(username=username).first():
            error = "Username already taken"
        elif User.query.filter_by(email=email).first():
            error = "Email already registered"
        elif password != confirm_password:
            error = "Passwords do not match"
        elif len(password) < 8:
            error = "Password must be at least 8 characters long"
        
        if error:
            flash(error, "danger")
        else:
            # Create new user
            user = User(username=username, email=email)
            user.set_password(password)
            user.generate_verification_token()
            
            # Add to database
            db.session.add(user)
            db.session.commit()
            
            # Send verification email
            email_utils.send_verification_email(user, get_base_url())
            
            flash("Registration successful! Please check your email to verify your account.", "success")
            return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/verify/<token>')
def verify_email(token):
    """Verify email with token"""
    user = User.query.filter_by(verification_token=token).first()
    
    if not user:
        flash("Invalid or expired verification link", "danger")
        return redirect(url_for('login'))
    
    user.email_verified = True
    user.verification_token = None
    db.session.commit()
    
    flash("Email verified successfully! You can now log in.", "success")
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username_or_email = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        
        # Try to find user by username first, then by email
        user = User.query.filter_by(username=username_or_email).first()
        if not user:
            user = User.query.filter_by(email=username_or_email).first()
        
        if not user or not user.check_password(password):
            flash("Invalid username/email or password", "danger")
            return render_template('login.html')
        
        if not user.email_verified:
            flash("Please verify your email before logging in", "warning")
            return render_template('login.html')
        
        login_user(user, remember=remember)
        user.last_login = datetime.datetime.utcnow()
        db.session.commit()
        
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('dashboard')
        
        flash(f"Welcome back, {user.username}!", "success")
        return redirect(next_page)
    
    return render_template('login.html')

@app.route('/terms')
def terms():
    """Terms of Service page"""
    online_count = get_online_users_count()
    return render_template('terms.html', online_count=online_count)

@app.route('/logout')
@login_required
def logout():
    """Log out user"""
    logout_user()
    flash("You have been logged out", "info")
    return redirect(url_for('home'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Forgot password page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        
        if not email:
            flash("Please enter your email address", "danger")
            return render_template('forgot_password.html')
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            token = user.generate_reset_token()
            db.session.commit()
            
            email_utils.send_password_reset_email(user, get_base_url())
        
        # Always show success message to prevent email enumeration
        flash("If your email is registered, you will receive password reset instructions", "info")
        return redirect(url_for('login'))
    
    return render_template('forgot_password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password with token"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    user = User.query.filter_by(reset_token=token).first()
    
    if not user or not user.reset_token_expiry or user.reset_token_expiry < datetime.datetime.utcnow():
        flash("Invalid or expired reset link", "danger")
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not password or len(password) < 8:
            flash("Password must be at least 8 characters long", "danger")
        elif password != confirm_password:
            flash("Passwords do not match", "danger")
        else:
            user.set_password(password)
            user.reset_token = None
            user.reset_token_expiry = None
            db.session.commit()
            
            flash("Password reset successfully! You can now log in with your new password.", "success")
            return redirect(url_for('login'))
    
    return render_template('reset_password.html')

###############
# Main Routes #
###############

# CORS decorator for API endpoints
def add_cors_headers(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        resp = f(*args, **kwargs)
        
        # Check if the request is from GitHub Pages
        origin = request.headers.get('Origin', '')
        allowed_origins = [
            'https://somerandomfella.github.io',
            'http://localhost:8000',  # For local testing
            'http://127.0.0.1:8000'   # For local testing
        ]
        
        if origin in allowed_origins:
            resp.headers['Access-Control-Allow-Origin'] = origin
            resp.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
            resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        
        return resp
    return decorated_function

# API endpoints for GitHub Pages
@app.route('/api/tools', methods=['GET', 'OPTIONS'])
@add_cors_headers
def api_tools():
    """API endpoint to get all tools"""
    # Define all available tools
    all_tools = [
        {
            'name': 'Discord Typing Indicator',
            'description': 'Send continuous typing indicators to a Discord channel',
            'icon': 'typing-icon.svg',
            'url': f"{get_base_url()}/tool/typing",
            'category': 'presence'
        },
        {
            'name': 'Discord Status Changer',
            'description': 'Automatically change your Discord status',
            'icon': 'status-icon.svg',
            'url': f"{get_base_url()}/tool/status",
            'category': 'presence'
        },
        {
            'name': 'Discord Message Scheduler',
            'description': 'Schedule messages to be sent at specific times',
            'icon': 'message-icon.svg',
            'url': f"{get_base_url()}/tool/scheduler",
            'category': 'messaging'
        },
        {
            'name': 'Discord Voice Joiner',
            'description': 'Automatically join voice channels',
            'icon': 'voice-icon.svg', 
            'url': f"{get_base_url()}/tool/voice",
            'category': 'voice'
        },
        {
            'name': 'Discord Auto-Reactor',
            'description': 'Automatically react to messages with emojis',
            'icon': 'reaction-icon.svg',
            'url': f"{get_base_url()}/tool/reactor",
            'category': 'interactions'
        },
        {
            'name': 'Discord User Tracker',
            'description': 'Monitor when users come online or go offline',
            'icon': 'monitor-icon.svg',
            'url': f"{get_base_url()}/tool/tracker",
            'category': 'monitoring'
        },
        {
            'name': 'Discord Server Scanner',
            'description': 'Scan and analyze Discord server activity',
            'icon': 'monitor-icon.svg',
            'url': f"{get_base_url()}/tool/scanner",
            'category': 'monitoring'
        },
        {
            'name': 'Discord Channel Monitor',
            'description': 'Get notified of new messages in specific channels',
            'icon': 'message-icon.svg',
            'url': f"{get_base_url()}/tool/channel",
            'category': 'monitoring'
        },
        {
            'name': 'Discord DM Assistant',
            'description': 'Auto-respond to direct messages when you\'re away',
            'icon': 'message-icon.svg',
            'url': f"{get_base_url()}/tool/dm",
            'category': 'messaging'
        },
        {
            'name': 'Discord Mention Watcher',
            'description': 'Get alerts when you\'re mentioned in any channel',
            'icon': 'reaction-icon.svg',
            'url': f"{get_base_url()}/tool/mentions",
            'category': 'monitoring'
        },
        {
            'name': 'Discord Activity Simulator',
            'description': 'Simulate activity to maintain online status',
            'icon': 'status-icon.svg',
            'url': f"{get_base_url()}/tool/activity",
            'category': 'presence'
        },
        {
            'name': 'Discord Chat Logger',
            'description': 'Archive and save chat conversations automatically',
            'icon': 'message-icon.svg',
            'url': f"{get_base_url()}/tool/logger",
            'category': 'utilities'
        }
    ]
    
    # Select which tools to return (all or featured)
    featured_only = request.args.get('featured', 'false').lower() == 'true'
    result = all_tools[:6] if featured_only else all_tools
    
    return jsonify({
        'tools': result,
        'count': len(result),
        'total': len(all_tools)
    })

@app.route('/api/online-count', methods=['GET', 'OPTIONS'])
@add_cors_headers
def api_online_count():
    """API endpoint to get the number of online users"""
    count = get_online_users_count()
    return jsonify({
        'count': count
    })

@app.route('/')
def home():
    """Home page with list of featured tools"""
    online_count = get_online_users_count()
    
    # Define all available tools
    all_tools = [
        {
            'name': 'Discord Typing Indicator',
            'description': 'Send continuous typing indicators to a Discord channel',
            'icon': 'reaction-icon.svg',
            'url': url_for('dashboard')
        },
        {
            'name': 'Discord Status Changer',
            'description': 'Automatically change your Discord status',
            'icon': 'monitor-icon.svg',
            'url': '#'
        },
        {
            'name': 'Discord Message Scheduler',
            'description': 'Schedule messages to be sent at specific times',
            'icon': 'monitor-icon.svg',
            'url': '#'
        },
        {
            'name': 'Discord Voice Joiner',
            'description': 'Automatically join voice channels',
            'icon': 'message-icon.svg',
            'url': '#'
        },
        {
            'name': 'Discord Auto-Reactor',
            'description': 'Automatically react to messages with emojis',
            'icon': 'reaction-icon.svg',
            'url': '#'
        },
        {
            'name': 'Discord User Tracker',
            'description': 'Monitor when users come online or go offline',
            'icon': 'monitor-icon.svg',
            'url': '#'
        },
        {
            'name': 'Discord Server Scanner',
            'description': 'Scan and analyze Discord server activity',
            'icon': 'monitor-icon.svg',
            'url': '#'
        },
        {
            'name': 'Discord Channel Monitor',
            'description': 'Get notified of new messages in specific channels',
            'icon': 'message-icon.svg',
            'url': '#'
        },
        {
            'name': 'Discord DM Assistant',
            'description': 'Auto-respond to direct messages when you\'re away',
            'icon': 'reaction-icon.svg',
            'url': '#'
        },
        {
            'name': 'Discord Mention Watcher',
            'description': 'Get alerts when you\'re mentioned in any channel',
            'icon': 'monitor-icon.svg',
            'url': '#'
        },
        {
            'name': 'Discord Activity Simulator',
            'description': 'Simulate activity to maintain online status',
            'icon': 'monitor-icon.svg',
            'url': '#'
        },
        {
            'name': 'Discord Chat Logger',
            'description': 'Archive and save chat conversations automatically',
            'icon': 'message-icon.svg',
            'url': '#'
        }
    ]
    
    # Only show the first 6 tools on the home page
    featured_tools = all_tools[:6]
    
    return render_template('home.html', featured_tools=featured_tools, online_count=online_count)

@app.route('/all_tools')
def all_tools():
    """Page showing all available tools"""
    online_count = get_online_users_count()
    
    # Define all available tools
    all_tools = [
        {
            'name': 'Discord Typing Indicator',
            'description': 'Send continuous typing indicators to a Discord channel',
            'icon': 'reaction-icon.svg',
            'url': url_for('dashboard')
        },
        {
            'name': 'Discord Status Changer',
            'description': 'Automatically change your Discord status',
            'icon': 'monitor-icon.svg',
            'url': '#'
        },
        {
            'name': 'Discord Message Scheduler',
            'description': 'Schedule messages to be sent at specific times',
            'icon': 'monitor-icon.svg',
            'url': '#'
        },
        {
            'name': 'Discord Voice Joiner',
            'description': 'Automatically join voice channels',
            'icon': 'message-icon.svg',
            'url': '#'
        },
        {
            'name': 'Discord Auto-Reactor',
            'description': 'Automatically react to messages with emojis',
            'icon': 'reaction-icon.svg',
            'url': '#'
        },
        {
            'name': 'Discord User Tracker',
            'description': 'Monitor when users come online or go offline',
            'icon': 'monitor-icon.svg',
            'url': '#'
        },
        {
            'name': 'Discord Server Scanner',
            'description': 'Scan and analyze Discord server activity',
            'icon': 'monitor-icon.svg',
            'url': '#'
        },
        {
            'name': 'Discord Channel Monitor',
            'description': 'Get notified of new messages in specific channels',
            'icon': 'message-icon.svg',
            'url': '#'
        },
        {
            'name': 'Discord DM Assistant',
            'description': 'Auto-respond to direct messages when you\'re away',
            'icon': 'message-icon.svg',
            'url': '#'
        },
        {
            'name': 'Discord Mention Watcher',
            'description': 'Get alerts when you\'re mentioned in any channel',
            'icon': 'reaction-icon.svg',
            'url': '#'
        },
        {
            'name': 'Discord Activity Simulator',
            'description': 'Simulate activity to maintain online status',
            'icon': 'monitor-icon.svg',
            'url': '#'
        },
        {
            'name': 'Discord Chat Logger',
            'description': 'Archive and save chat conversations automatically',
            'icon': 'message-icon.svg',
            'url': '#'
        }
    ]
    
    return render_template('all_tools.html', all_tools=all_tools, online_count=online_count)

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard page showing running tools"""
    online_count = get_online_users_count()
    
    # Get user's tools
    tools = RunningTool.query.filter_by(user_id=current_user.id).all()
    
    # Get bot configuration
    bot_config = {
        'typing_interval': config.TYPING_INTERVAL,
        'log_level': config.LOG_LEVEL,
        'max_restart_attempts': config.MAX_RESTART_ATTEMPTS,
        'restart_cooldown': config.RESTART_COOLDOWN,
    }
    
    # Check status of each tool
    for tool in tools:
        if tool.status == 'running':
            try:
                if tool.process_id:
                    process = psutil.Process(tool.process_id)
                    if not process.is_running():
                        tool.status = 'crashed'
                        db.session.commit()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                tool.status = 'crashed'
                db.session.commit()
    
    return render_template('dashboard.html', 
                          tools=tools,
                          bot_config=bot_config,
                          online_count=online_count)

@app.route('/tool/<int:tool_id>')
@login_required
def tool_details(tool_id):
    """Tool details page"""
    tool = RunningTool.query.filter_by(id=tool_id, user_id=current_user.id).first_or_404()
    
    # Get logs for this tool
    logs = get_bot_logs(tool_id, limit=20)
    
    # Check if process is running
    running = False
    uptime = None
    
    if tool.status == 'running' and tool.process_id:
        try:
            process = psutil.Process(tool.process_id)
            if process.is_running():
                running = True
                uptime = time.time() - tool.created_at.timestamp()
                uptime = format_uptime(uptime)
            else:
                tool.status = 'crashed'
                db.session.commit()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            tool.status = 'crashed'
            db.session.commit()
    
    return render_template('tool_details.html', 
                          tool=tool,
                          logs=logs,
                          running=running,
                          uptime=uptime)

###############
# Tool Routes #
###############

@app.route('/start', methods=['POST'])
@login_required
def start_bot():
    """Start a Discord bot"""
    # Get bot type from form
    bot_type = request.form.get('bot_type', 'discord')
    channel_id = request.form.get('channel_id')
    leave_running = request.form.get('leave_running') == 'on'
    
    # Additional anti-detection options for user token
    random_intervals = request.form.get('random_intervals') == 'on'
    min_interval = request.form.get('min_interval', 5)
    max_interval = request.form.get('max_interval', 15)
    random_breaks = request.form.get('random_breaks') == 'on'
    break_chance = request.form.get('break_chance', 5)
    min_break = request.form.get('min_break', 30)
    max_break = request.form.get('max_break', 300)
    
    try:
        # Validate channel ID
        if not channel_id:
            flash("Channel ID is required", "danger")
            return redirect(url_for('dashboard'))
        
        # Create tool record
        tool = RunningTool(
            user_id=current_user.id,
            tool_type=bot_type,
            channel_id=channel_id,
            status='running',
            random_intervals=random_intervals,
            min_interval=min_interval,
            max_interval=max_interval,
            random_breaks=random_breaks,
            break_chance=float(break_chance) / 100,  # Convert percentage to decimal
            min_break=min_break,
            max_break=max_break
        )
        
        db.session.add(tool)
        db.session.commit()
        
        # Store config for this tool
        tool_config = {
            'channel_id': channel_id,
            'leave_running': leave_running,
            'random_intervals': random_intervals,
            'min_interval': min_interval,
            'max_interval': max_interval,
            'random_breaks': random_breaks,
            'break_chance': break_chance,
            'min_break': min_break,
            'max_break': max_break
        }
        
        # Convert to JSON string
        tool.config = tool_config
        db.session.commit()
        
        # Start bot process
        cmd = ['python', 'start.py', bot_type, str(tool.id)]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        
        # Update process ID
        tool.process_id = process.pid
        db.session.commit()
        
        # Log start
        add_bot_log(tool.id, f"Started {bot_type} typing indicator for channel {channel_id}")
        
        flash(f"Started {bot_type} typing indicator", "success")
    except Exception as e:
        logger.error(f"Error starting bot: {str(e)}")
        flash(f"Error starting bot: {str(e)}", "danger")
    
    return redirect(url_for('dashboard'))

@app.route('/stop/<int:tool_id>', methods=['POST'])
@login_required
def stop_bot(tool_id):
    """Stop a running bot"""
    tool = RunningTool.query.filter_by(id=tool_id, user_id=current_user.id).first_or_404()
    
    if tool.status != 'running':
        flash("Tool is not running", "warning")
        return redirect(url_for('dashboard'))
    
    try:
        if tool.process_id:
            process = psutil.Process(tool.process_id)
            children = process.children(recursive=True)
            
            # Terminate child processes
            for child in children:
                child.terminate()
            
            # Give them time to terminate
            gone, alive = psutil.wait_procs(children, timeout=3)
            
            # Kill if still alive
            for p in alive:
                p.kill()
            
            # Terminate main process
            process.terminate()
            process.wait(timeout=3)
            
            # Update tool status
            tool.status = 'stopped'
            db.session.commit()
            
            # Log stop
            add_bot_log(tool.id, "Stopped by user", level="INFO")
            
            flash("Typing indicator stopped successfully", "success")
        else:
            flash("No process ID found for this tool", "warning")
            tool.status = 'stopped'
            db.session.commit()
    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
        logger.error(f"Error stopping bot: {str(e)}")
        flash(f"Error stopping bot: Process no longer exists", "info")
        tool.status = 'stopped'
        db.session.commit()
    
    return redirect(url_for('dashboard'))

@app.route('/restart/<int:tool_id>', methods=['POST'])
@login_required
def restart_bot(tool_id):
    """Restart a bot"""
    tool = RunningTool.query.filter_by(id=tool_id, user_id=current_user.id).first_or_404()
    
    # Stop the tool first
    try:
        if tool.process_id:
            try:
                process = psutil.Process(tool.process_id)
                process.terminate()
                process.wait(timeout=3)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except Exception as e:
        logger.error(f"Error stopping bot for restart: {str(e)}")
    
    # Start the tool again
    try:
        cmd = ['python', 'start.py', tool.tool_type, str(tool.id)]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        
        # Update process ID and status
        tool.process_id = process.pid
        tool.status = 'running'
        tool.updated_at = datetime.datetime.utcnow()
        db.session.commit()
        
        # Log restart
        add_bot_log(tool.id, "Restarted by user", level="INFO")
        
        flash("Typing indicator restarted successfully", "success")
    except Exception as e:
        logger.error(f"Error restarting bot: {str(e)}")
        flash(f"Error restarting bot: {str(e)}", "danger")
    
    return redirect(url_for('dashboard'))

@app.route('/delete/<int:tool_id>', methods=['POST'])
@login_required
def delete_tool(tool_id):
    """Delete a tool"""
    tool = RunningTool.query.filter_by(id=tool_id, user_id=current_user.id).first_or_404()
    
    # Stop the process if it's running
    try:
        if tool.status == 'running' and tool.process_id:
            try:
                process = psutil.Process(tool.process_id)
                process.terminate()
                process.wait(timeout=3)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except Exception as e:
        logger.error(f"Error stopping bot for deletion: {str(e)}")
    
    # Delete logs
    ToolLog.query.filter_by(tool_id=tool.id).delete()
    
    # Delete tool
    db.session.delete(tool)
    db.session.commit()
    
    flash("Typing indicator deleted successfully", "success")
    return redirect(url_for('dashboard'))

@app.route('/update-config/<int:tool_id>', methods=['POST'])
@login_required
def update_tool_config(tool_id):
    """Update configuration for a specific tool"""
    tool = RunningTool.query.filter_by(id=tool_id, user_id=current_user.id).first_or_404()
    
    # Get form data
    random_intervals = request.form.get('random_intervals') == 'on'
    min_interval = request.form.get('min_interval', 5)
    max_interval = request.form.get('max_interval', 15)
    random_breaks = request.form.get('random_breaks') == 'on'
    break_chance = request.form.get('break_chance', 5)
    min_break = request.form.get('min_break', 30)
    max_break = request.form.get('max_break', 300)
    
    try:
        # Update tool
        tool.random_intervals = random_intervals
        tool.min_interval = min_interval
        tool.max_interval = max_interval
        tool.random_breaks = random_breaks
        tool.break_chance = float(break_chance) / 100  # Convert percentage to decimal
        tool.min_break = min_break
        tool.max_break = max_break
        
        # Update config
        config = tool.config or {}
        config.update({
            'random_intervals': random_intervals,
            'min_interval': min_interval,
            'max_interval': max_interval,
            'random_breaks': random_breaks,
            'break_chance': break_chance,
            'min_break': min_break,
            'max_break': max_break
        })
        tool.config = config
        
        db.session.commit()
        
        add_bot_log(tool.id, "Configuration updated by user", level="INFO")
        flash("Configuration updated successfully", "success")
        
        # Restart needed?
        if tool.status == 'running':
            flash("Please restart the tool for changes to take effect", "info")
    except Exception as e:
        logger.error(f"Error updating tool config: {str(e)}")
        flash(f"Error updating configuration: {str(e)}", "danger")
    
    return redirect(url_for('tool_details', tool_id=tool_id))

@app.route('/update-env', methods=['POST'])
@login_required
def update_env():
    """Update .env configuration"""
    # Get form data
    typing_interval = request.form.get('typing_interval')
    log_level = request.form.get('log_level')
    max_restart_attempts = request.form.get('max_restart_attempts')
    restart_cooldown = request.form.get('restart_cooldown')
    
    try:
        # Create .env file if it doesn't exist
        if not os.path.exists('.env'):
            # Copy from .env.example
            if os.path.exists('.env.example'):
                with open('.env.example', 'r') as f:
                    env_lines = f.readlines()
            else:
                # Create a minimal .env
                env_lines = [
                    "BOT_TOKEN=\n",
                    "CHANNEL_ID=\n",
                    "USER_TOKEN=\n",
                    "TYPING_INTERVAL=8\n",
                    "LOG_LEVEL=INFO\n",
                    "MAX_RESTART_ATTEMPTS=0\n",
                    "RESTART_COOLDOWN=10\n",
                    "SESSION_SECRET=development_secret_key\n"
                ]
        else:
            # Read existing .env
            with open('.env', 'r') as f:
                env_lines = f.readlines()
        
        # Update values
        updated_lines = []
        found_keys = set()
        
        for line in env_lines:
            if line.startswith('TYPING_INTERVAL=') and typing_interval:
                updated_lines.append(f'TYPING_INTERVAL={typing_interval}\n')
                found_keys.add('TYPING_INTERVAL')
            elif line.startswith('LOG_LEVEL=') and log_level:
                updated_lines.append(f'LOG_LEVEL={log_level}\n')
                found_keys.add('LOG_LEVEL')
            elif line.startswith('MAX_RESTART_ATTEMPTS=') and max_restart_attempts:
                updated_lines.append(f'MAX_RESTART_ATTEMPTS={max_restart_attempts}\n')
                found_keys.add('MAX_RESTART_ATTEMPTS')
            elif line.startswith('RESTART_COOLDOWN=') and restart_cooldown:
                updated_lines.append(f'RESTART_COOLDOWN={restart_cooldown}\n')
                found_keys.add('RESTART_COOLDOWN')
            else:
                updated_lines.append(line)
        
        # Add any missing keys
        if typing_interval and 'TYPING_INTERVAL' not in found_keys:
            updated_lines.append(f'TYPING_INTERVAL={typing_interval}\n')
        if log_level and 'LOG_LEVEL' not in found_keys:
            updated_lines.append(f'LOG_LEVEL={log_level}\n')
        if max_restart_attempts and 'MAX_RESTART_ATTEMPTS' not in found_keys:
            updated_lines.append(f'MAX_RESTART_ATTEMPTS={max_restart_attempts}\n')
        if restart_cooldown and 'RESTART_COOLDOWN' not in found_keys:
            updated_lines.append(f'RESTART_COOLDOWN={restart_cooldown}\n')
        
        with open('.env', 'w') as f:
            f.writelines(updated_lines)
        
        flash("Global configuration updated successfully", "success")
        
        # Reload configuration
        load_dotenv(override=True)
        
    except Exception as e:
        logger.error(f"Error updating configuration: {str(e)}")
        flash(f"Error updating configuration: {str(e)}", "danger")
    
    return redirect(url_for('dashboard'))

@app.route('/upload-credentials', methods=['POST'])
@login_required
def upload_credentials():
    """Process the uploaded credentials file"""
    if 'credentials_file' not in request.files:
        flash("No file uploaded", "danger")
        return redirect(url_for('dashboard'))
    
    file = request.files['credentials_file']
    
    if file.filename == '':
        flash("No file selected", "danger")
        return redirect(url_for('dashboard'))
    
    if not (file.filename.endswith('.txt') or file.filename.endswith('.env')):
        flash("Only .txt or .env files are allowed", "danger")
        return redirect(url_for('dashboard'))
    
    try:
        # Read the file content
        file_content = file.read().decode('utf-8')
        
        # Update environment variables
        update_env_from_content(file_content)
        
        flash("Discord credentials loaded successfully", "success")
    except Exception as e:
        logger.error(f"Error processing credentials file: {str(e)}")
        flash(f"Error processing file: {str(e)}", "danger")
    
    return redirect(url_for('dashboard'))

@app.route('/direct-env-update', methods=['POST'])
@login_required
def direct_env_update():
    """Process the manually entered credentials"""
    try:
        # Get values from form
        channel_id = request.form.get('channel_id')
        use_bot_token = request.form.get('use_bot_token') == 'on'
        bot_token = request.form.get('bot_token')
        user_token = request.form.get('user_token')
        
        # Build env content
        env_lines = []
        
        if channel_id:
            env_lines.append(f"CHANNEL_ID={channel_id}\n")
        
        if use_bot_token and bot_token:
            env_lines.append(f"BOT_TOKEN={bot_token}\n")
        elif not use_bot_token and user_token:
            env_lines.append(f"USER_TOKEN={user_token}\n")
        
        if env_lines:
            # Update environment variables
            update_env_from_content(''.join(env_lines))
            flash("Discord credentials saved successfully", "success")
        else:
            flash("No credentials provided", "warning")
    
    except Exception as e:
        logger.error(f"Error saving credentials: {str(e)}")
        flash(f"Error saving credentials: {str(e)}", "danger")
    
    return redirect(url_for('dashboard'))

def update_env_from_content(content):
    """Update .env file with the provided content"""
    # Create .env file if it doesn't exist
    if not os.path.exists('.env'):
        # Copy from .env.example
        if os.path.exists('.env.example'):
            with open('.env.example', 'r') as f:
                env_lines = f.readlines()
        else:
            # Create a minimal .env
            env_lines = [
                "BOT_TOKEN=\n",
                "CHANNEL_ID=\n",
                "USER_TOKEN=\n",
                "TYPING_INTERVAL=8\n",
                "LOG_LEVEL=INFO\n",
                "MAX_RESTART_ATTEMPTS=0\n",
                "RESTART_COOLDOWN=10\n",
                "SESSION_SECRET=development_secret_key\n"
            ]
    else:
        # Read existing .env
        with open('.env', 'r') as f:
            env_lines = f.readlines()
    
    # Process uploaded content
    values_to_update = {}
    for line in content.splitlines():
        line = line.strip()
        if line and '=' in line and not line.startswith('#'):
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()
            
            # Only update tokens and channel ID
            if key in ['BOT_TOKEN', 'USER_TOKEN', 'CHANNEL_ID'] and value:
                values_to_update[key] = value
    
    # Update .env file
    if values_to_update:
        updated_lines = []
        found_keys = set()
        
        for line in env_lines:
            for key in values_to_update:
                if line.startswith(f"{key}="):
                    updated_lines.append(f"{key}={values_to_update[key]}\n")
                    found_keys.add(key)
                    break
            else:
                updated_lines.append(line)
        
        # Add any keys that weren't in the original file
        for key, value in values_to_update.items():
            if key not in found_keys:
                updated_lines.append(f"{key}={value}\n")
        
        # Write updated lines back to .env
        with open('.env', 'w') as f:
            f.writelines(updated_lines)
        
        # Reload environment variables
        load_dotenv(override=True)

@app.route('/logs/<int:tool_id>')
@login_required
def get_logs(tool_id):
    """Get logs for a tool as JSON"""
    tool = RunningTool.query.filter_by(id=tool_id, user_id=current_user.id).first_or_404()
    logs = get_bot_logs(tool_id, limit=50)
    
    log_data = [{
        'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'level': log.level,
        'message': log.message
    } for log in logs]
    
    return jsonify(logs=log_data)

# Create database tables on startup
with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)