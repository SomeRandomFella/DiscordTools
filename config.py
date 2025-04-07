#!/usr/bin/env python3
import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bot settings
BOT_TOKEN = os.environ.get('BOT_TOKEN')
USER_TOKEN = os.environ.get('USER_TOKEN')
CHANNEL_ID = os.environ.get('CHANNEL_ID')
TYPING_INTERVAL = int(os.environ.get('TYPING_INTERVAL', 8))
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
MAX_RESTART_ATTEMPTS = int(os.environ.get('MAX_RESTART_ATTEMPTS', 0))
RESTART_COOLDOWN = int(os.environ.get('RESTART_COOLDOWN', 10))

# Convert log level string to numeric value
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

LOG_LEVEL_NUM = LOG_LEVELS.get(LOG_LEVEL, logging.INFO)