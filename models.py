import datetime
from flask_login import UserMixin
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash
from main import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    email_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(100), nullable=True)
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)
    running_tools = db.relationship('RunningTool', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_verification_token(self):
        import secrets
        self.verification_token = secrets.token_urlsafe(32)
        return self.verification_token
    
    def generate_reset_token(self):
        import secrets
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expiry = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        return self.reset_token


class RunningTool(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tool_type = db.Column(db.String(20), nullable=False)  # 'discord_bot' or 'user_token'
    status = db.Column(db.String(20), default='running')  # 'running', 'stopped', 'crashed', 'rate_limited'
    process_id = db.Column(db.Integer, nullable=True)
    channel_id = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    config = db.Column(db.JSON, nullable=True)  # For storing tool-specific configuration
    logs = db.relationship('ToolLog', backref='tool', lazy='dynamic')
    
    # Anti-detection features (for user token tools)
    random_intervals = db.Column(db.Boolean, default=False)
    min_interval = db.Column(db.Integer, default=5)  # seconds
    max_interval = db.Column(db.Integer, default=15)  # seconds
    random_breaks = db.Column(db.Boolean, default=False)
    break_chance = db.Column(db.Float, default=0.05)  # 5% chance each interval
    min_break = db.Column(db.Integer, default=30)  # seconds
    max_break = db.Column(db.Integer, default=300)  # seconds


class ToolLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tool_id = db.Column(db.Integer, db.ForeignKey('running_tool.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    level = db.Column(db.String(10), default='INFO')  # 'INFO', 'WARNING', 'ERROR'
    message = db.Column(db.Text, nullable=False)