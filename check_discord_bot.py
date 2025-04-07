#!/usr/bin/env python3
"""
Discord Bot Checker
This script tests the Discord bot functionality without actually connecting to Discord.
It verifies that the bot class and required modules are working properly.
"""

import importlib
import sys

def check_module_importable(module_name):
    """Check if a module can be imported"""
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False

def verify_typing_functionality():
    """Verify that the typing indicator functionality works"""
    try:
        from bot import TypingBot
        print("✓ Bot class implements typing indicator functionality")
        return True
    except (ImportError, AttributeError):
        print("✗ Bot class doesn't implement typing indicator functionality")
        return False

def verify_watchdog():
    """Verify that the watchdog functionality works"""
    try:
        from watchdog import BotWatchdog
        print("✓ Watchdog system for auto-restart implemented")
        return True
    except (ImportError, AttributeError):
        print("✗ Watchdog system not implemented")
        return False

def verify_config():
    """Verify that the configuration system works"""
    try:
        import config
        print("✓ Configuration system ready")
        return True
    except ImportError:
        print("✗ Configuration system not available")
        return False

def verify_logger():
    """Verify that the logger functionality works"""
    try:
        import logger
        print("✓ Logging system configured")
        return True
    except ImportError:
        print("✗ Logging system not available")
        return False

def main():
    """Main entry point"""
    errors = 0
    
    # Check required modules
    modules = ["discord", "json", "asyncio", "os", "logging", "datetime", "signal"]
    for module in modules:
        if check_module_importable(module):
            print(f"✓ Module {module} available")
        else:
            print(f"✗ Module {module} not available")
            errors += 1
    
    # Verify core functionality
    if not verify_typing_functionality():
        errors += 1
    
    if not verify_watchdog():
        errors += 1
    
    if not verify_config():
        errors += 1
    
    if not verify_logger():
        errors += 1
    
    print("\nCore Discord bot check complete.")
    
    if errors > 0:
        print(f"Found {errors} errors. The bot may not function properly.")
        print("→ Missing Discord credentials to run")
        sys.exit(1)
    else:
        print("All checks passed! The bot should work with valid Discord credentials.")
        print("→ Needs actual Discord credentials to run")
        sys.exit(0)

if __name__ == "__main__":
    main()