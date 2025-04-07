#!/usr/bin/env python3
"""
Discord Tools Suite Configuration Helper
This script helps configure and start the Discord Tools Suite
and serves as a replacement for the .replit configuration

Usage:
    python discord_tools_config.py [command]

Commands:
    run         - Start the web application server
    dev         - Start the server in development mode
    check       - Check if all required dependencies are installed
    test        - Run tests
    help        - Show this help message
"""

import os
import sys
import subprocess
import argparse

def run_server():
    """Start the web application server using gunicorn"""
    cmd = ["gunicorn", "--bind", "0.0.0.0:5000", "--reuse-port", "--reload", "main:app"]
    
    try:
        print("Starting Discord Tools Suite web server...")
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except subprocess.CalledProcessError as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        "discord-py",
        "flask",
        "flask-login",
        "flask-sqlalchemy",
        "flask-wtf",
        "gunicorn",
        "psutil",
        "python-dotenv",
        "requests",
        "sendgrid",
        "werkzeug"
    ]
    
    print("Checking required dependencies...")
    missing = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package}")
            missing.append(package)
    
    if missing:
        print("\nMissing packages:")
        print(", ".join(missing))
        install = input("Install missing packages? (y/n): ")
        if install.lower() == 'y':
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
    else:
        print("\nAll required dependencies are installed.")

def run_tests():
    """Run tests for the Discord Tools Suite"""
    cmd = ["python", "-m", "unittest", "discover", "-s", "tests"]
    
    try:
        print("Running tests...")
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Tests failed: {e}")
        sys.exit(1)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Discord Tools Suite Configuration Helper")
    parser.add_argument('command', nargs='?', default='run', 
                        choices=['run', 'dev', 'check', 'test', 'help'],
                        help='Command to execute')
    
    args = parser.parse_args()
    
    if args.command == 'run':
        run_server()
    elif args.command == 'dev':
        os.environ['FLASK_ENV'] = 'development'
        os.environ['FLASK_DEBUG'] = '1'
        run_server()
    elif args.command == 'check':
        check_dependencies()
    elif args.command == 'test':
        run_tests()
    elif args.command == 'help':
        print(__doc__)
    
if __name__ == "__main__":
    main()