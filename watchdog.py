#!/usr/bin/env python3
import subprocess
import sys
import time
import signal
import logging
import psutil
import os

from config import MAX_RESTART_ATTEMPTS, RESTART_COOLDOWN
from logger import logger

class BotWatchdog:
    """
    Watchdog class that monitors and automatically restarts the Discord bot if it crashes.
    Can monitor either the official bot or the user typing bot.
    """
    
    def __init__(self, bot_type="discord"):
        """
        Initialize the watchdog
        
        Args:
            bot_type: Type of bot to monitor - either "discord" for discord.py bot
                     or "user" for the user token typing bot
        """
        self.bot_type = bot_type
        self.process = None
        self.restart_count = 0
        self.max_restart_attempts = MAX_RESTART_ATTEMPTS
        self.restart_cooldown = RESTART_COOLDOWN
        self.running = False
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, sig, frame):
        """Handle keyboard interrupts to gracefully shut down the bot"""
        logger.info("Watchdog received shutdown signal")
        self.running = False
        
        if self.process:
            logger.info("Terminating bot process")
            try:
                # Get process object from pid
                process = psutil.Process(self.process.pid)
                children = process.children(recursive=True)
                
                # Terminate child processes
                for child in children:
                    child.terminate()
                
                # Wait a bit for processes to terminate
                gone, alive = psutil.wait_procs(children, timeout=3)
                
                # Kill any that are still alive
                for p in alive:
                    p.kill()
                
                # Terminate main process
                process.terminate()
                process.wait(timeout=3)
            except (psutil.NoSuchProcess, AttributeError):
                # Process is already gone
                pass
        
        sys.exit(0)
    
    def start_bot(self):
        """Start the bot as a subprocess"""
        script = "bot.py" if self.bot_type == "discord" else "usertyping.py"
        
        logger.info(f"Starting {self.bot_type} bot ({script})")
        
        # Start the bot process
        self.process = subprocess.Popen(
            [sys.executable, script],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        
        logger.info(f"Bot process started with PID {self.process.pid}")
        
        return self.process
    
    def monitor(self):
        """Monitor the bot process and restart it if it crashes"""
        logger.info(f"Starting watchdog for {self.bot_type} bot")
        logger.info(f"Max restart attempts: {'unlimited' if self.max_restart_attempts == 0 else self.max_restart_attempts}")
        logger.info(f"Restart cooldown: {self.restart_cooldown} seconds")
        
        self.running = True
        
        # Start the bot
        self.process = self.start_bot()
        
        # Monitor the process
        while self.running:
            # Check if the process is still running
            return_code = self.process.poll()
            
            if return_code is not None:
                # Process has terminated
                logger.warning(f"Bot process terminated with return code {return_code}")
                
                # Check if we should restart
                if self.max_restart_attempts == 0 or self.restart_count < self.max_restart_attempts:
                    self.restart_count += 1
                    logger.info(f"Restarting bot (attempt {self.restart_count})")
                    
                    # Wait before restarting
                    time.sleep(self.restart_cooldown)
                    
                    # Start the bot again
                    self.process = self.start_bot()
                else:
                    logger.error(f"Maximum restart attempts ({self.max_restart_attempts}) reached")
                    logger.error("Watchdog is stopping")
                    self.running = False
                    break
            
            # Sleep before checking again
            time.sleep(1)
        
        logger.info("Watchdog has stopped")

def main(bot_type=None):
    """
    Main entry point for the watchdog
    
    Args:
        bot_type: Type of bot to monitor - either "discord" for discord.py bot 
                 or "user" for the user token typing bot.
                 If None, it will be determined from command line arguments.
    """
    # Determine bot type from arguments if not provided
    if bot_type is None:
        bot_type = sys.argv[1] if len(sys.argv) > 1 else "discord"
    
    # Validate bot type
    if bot_type not in ["discord", "user"]:
        logger.error(f"Invalid bot type: {bot_type}")
        logger.error("Valid types are 'discord' or 'user'")
        return 1
    
    # Create and run the watchdog
    watchdog = BotWatchdog(bot_type)
    
    try:
        watchdog.monitor()
    except KeyboardInterrupt:
        logger.info("Watchdog stopped by user")
    except Exception as e:
        logger.error(f"Watchdog crashed: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())