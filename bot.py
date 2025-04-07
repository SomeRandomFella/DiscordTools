#!/usr/bin/env python3
import os
import asyncio
import discord
from discord.ext import commands
import time
import sys
import signal
from logger import logger
from config import BOT_TOKEN, CHANNEL_ID, TYPING_INTERVAL

# Configure Discord intents
intents = discord.Intents.default()
intents.typing = True
intents.message_content = True

class TypingBot(commands.Bot):
    def __init__(self):
        """Initialize the bot with required intents and command prefix"""
        super().__init__(command_prefix='!', intents=intents)
        self.target_channel_id = int(CHANNEL_ID) if CHANNEL_ID else None
        self.interval = TYPING_INTERVAL
        self.typing_task = None
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, lambda s, f: self.loop.create_task(self.close()))
        signal.signal(signal.SIGTERM, lambda s, f: self.loop.create_task(self.close()))
    
    async def on_ready(self):
        """Called when the bot is ready and connected to Discord"""
        logger.info(f"Bot connected as {self.user.name} (ID: {self.user.id})")
        logger.info(f"Using typing interval of {self.interval} seconds")
        
        if not self.target_channel_id:
            logger.error("No target channel ID specified. Please set the CHANNEL_ID environment variable.")
            await self.close()
            return
        
        # Start typing indicator task
        await self.before_typing()
    
    async def send_typing_indicator(self):
        """Sends a typing indicator to the target channel every TYPING_INTERVAL seconds"""
        # Get the channel
        channel = self.get_channel(self.target_channel_id)
        
        if not channel:
            logger.error(f"Could not find channel with ID {self.target_channel_id}")
            return
        
        logger.info(f"Starting typing indicator loop in channel: {channel.name} (ID: {channel.id})")
        
        while not self.is_closed():
            try:
                # Send typing indicator
                async with channel.typing():
                    logger.info(f"Sent typing indicator to {channel.name}")
                    # Sleep for the interval duration
                    await asyncio.sleep(self.interval)
            except discord.errors.Forbidden:
                logger.error("Bot does not have permission to send typing indicators in this channel")
                await asyncio.sleep(self.interval * 2)  # Wait longer on permission errors
            except discord.errors.HTTPException as e:
                logger.error(f"HTTP error: {str(e)}")
                await asyncio.sleep(self.interval)
            except Exception as e:
                logger.error(f"Error sending typing indicator: {str(e)}")
                await asyncio.sleep(self.interval)
    
    async def before_typing(self):
        """Ensures the bot is ready before starting the typing loop"""
        # Wait until the bot is fully connected
        while not self.is_ready():
            await asyncio.sleep(1)
        
        # Start the typing loop
        self.typing_task = self.loop.create_task(self.send_typing_indicator())
    
    async def on_error(self, event, *args, **kwargs):
        """Global error handler for all events"""
        logger.error(f"Error in event {event}: {sys.exc_info()[1]}")
    
    async def run_bot(self):
        """Run the bot with error handling"""
        try:
            logger.info("Starting bot...")
            await self.start(BOT_TOKEN)
        except discord.errors.LoginFailure:
            logger.error("Invalid bot token. Please check your BOT_TOKEN environment variable.")
            return 1
        except Exception as e:
            logger.error(f"Error starting bot: {str(e)}")
            return 1
        finally:
            if not self.is_closed():
                await self.close()
        
        return 0

async def main():
    """Main entry point for the bot"""
    if not BOT_TOKEN:
        logger.error("No bot token found. Please set the BOT_TOKEN environment variable.")
        return 1
    
    bot = TypingBot()
    return await bot.run_bot()

if __name__ == "__main__":
    # Run the async main function
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    exit_code = asyncio.run(main())
    sys.exit(exit_code)