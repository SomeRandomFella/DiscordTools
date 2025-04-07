#!/usr/bin/env python3
import requests
import time
import signal
import sys
import os
from config import USER_TOKEN, CHANNEL_ID, TYPING_INTERVAL
from logger import logger

class UserTypingBot:
    """
    A bot that uses a Discord user token to send typing indicators continuously.
    This is different from the bot.py which uses an official Discord bot token.
    """
    
    def __init__(self, user_token, channel_id):
        """
        Initialize the bot with user token and channel ID
        
        Args:
            user_token (str): Discord user token
            channel_id (str): Discord channel ID where typing indicators will be sent
        """
        self.user_token = user_token
        self.channel_id = channel_id
        self.interval = TYPING_INTERVAL
        self.running = False
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, sig, frame):
        """Handle signals to allow for graceful shutdown"""
        logger.info("Received signal to shut down")
        self.running = False
        sys.exit(0)
    
    def send_typing(self):
        """Send a single typing indicator to the channel"""
        headers = {
            'Authorization': self.user_token,
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(
                f'https://discord.com/api/v9/channels/{self.channel_id}/typing',
                headers=headers
            )
            
            if response.status_code == 204:
                logger.info(f"Sent typing indicator to channel {self.channel_id}")
                return True
            else:
                logger.error(f"Failed to send typing indicator: {response.status_code} - {response.text}")
                return False
        
        except Exception as e:
            logger.error(f"Error sending typing indicator: {str(e)}")
            return False
    
    def run(self):
        """Run the typing indicator bot in a continuous loop"""
        logger.info(f"Starting user typing bot for channel {self.channel_id}")
        logger.info(f"Using typing interval of {self.interval} seconds")
        
        self.running = True
        
        while self.running:
            success = self.send_typing()
            
            # If we couldn't send the typing indicator, wait a bit longer before retrying
            if not success:
                time.sleep(self.interval * 2)
            else:
                time.sleep(self.interval)

def main():
    """Main function to run the user typing bot"""
    # Check if we have the required configuration
    if not USER_TOKEN:
        logger.error("No user token found. Please set the USER_TOKEN environment variable.")
        return 1
    
    if not CHANNEL_ID:
        logger.error("No channel ID found. Please set the CHANNEL_ID environment variable.")
        return 1
    
    # Create and run the bot
    bot = UserTypingBot(USER_TOKEN, CHANNEL_ID)
    
    try:
        bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())