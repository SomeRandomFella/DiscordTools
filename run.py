#!/usr/bin/env python3
"""
Run script for Discord Tools Suite
This script starts the web application server using gunicorn
"""

import os
import subprocess
import sys

def main():
    """Main entry point for running the Discord Tools Suite"""
    # Set environment variables if needed
    if not os.environ.get('FLASK_ENV'):
        os.environ['FLASK_ENV'] = 'development'
    
    # Check if gunicorn is available
    try:
        import gunicorn
    except ImportError:
        print("Gunicorn is not installed. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "gunicorn"])
    
    # Start the server with gunicorn
    cmd = ["gunicorn", "--bind", "0.0.0.0:5000", "--reuse-port", "--reload", "main:app"]
    
    try:
        print("Starting Discord Tools Suite web server...")
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except subprocess.CalledProcessError as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()