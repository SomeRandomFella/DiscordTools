#!/usr/bin/env python3
import os
import logging
import datetime
from config import LOG_LEVEL_NUM

def setup_logger():
    """Configure the logger"""
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Create a formatted timestamp for the log filename
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = f'logs/discord_bot_{timestamp}.log'
    
    # Configure the logger
    logging.basicConfig(
        level=LOG_LEVEL_NUM,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger('discord_bot')

# Initialize the logger
logger = setup_logger()