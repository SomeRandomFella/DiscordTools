#!/usr/bin/env python3
"""
Check Workflow Configuration
This script creates a properly formatted workflow configuration and makes it executable
"""

import os
import subprocess

def main():
    """Main entry point"""
    # Create workflow directory if it doesn't exist
    os.makedirs('.workflow', exist_ok=True)
    
    # Create or update workflow check script
    with open('.workflow/check_discord_bot', 'w') as f:
        f.write('#!/bin/bash\n')
        f.write('python3 discord_bot_check.py\n')
    
    # Make the script executable
    subprocess.run(['chmod', '+x', '.workflow/check_discord_bot'])
    
    print("Workflow configuration updated successfully.")

if __name__ == "__main__":
    main()
