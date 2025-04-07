#!/usr/bin/env python3
import os
import sys
import argparse
from config import BOT_TOKEN, USER_TOKEN, CHANNEL_ID
from logger import logger
import watchdog

def check_configuration():
    """Check if the necessary configuration is available"""
    missing = []
    
    if not CHANNEL_ID:
        missing.append("CHANNEL_ID")
    
    return missing

def main():
    """Main entry point for the application"""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Discord Typing Indicator Bot")
    parser.add_argument("bot_type", nargs="?", default="discord", choices=["discord", "user"],
                       help="Type of bot to use: 'discord' (official bot) or 'user' (user token)")
    args = parser.parse_args()
    
    # Get the bot type
    bot_type = args.bot_type.lower()
    
    # Check configuration
    missing = check_configuration()
    
    # Also check for the specific token based on bot type
    if bot_type == "discord" and not BOT_TOKEN:
        missing.append("BOT_TOKEN")
    elif bot_type == "user" and not USER_TOKEN:
        missing.append("USER_TOKEN")
    
    if missing:
        logger.error(f"Missing configuration: {', '.join(missing)}")
        logger.error("Please set the required environment variables in .env file")
        return 1
    
    # Start the bot with watchdog
    return watchdog.main(bot_type)

if __name__ == "__main__":
    sys.exit(main())