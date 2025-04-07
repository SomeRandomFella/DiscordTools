# Discord Tools Suite

A comprehensive suite of Discord automation tools with a focus on channel presence and engagement. Our flagship typing indicator tool comes with automatic crash recovery, anti-detection measures, and a fully-featured web dashboard.

Now with GitHub Pages compatibility! Access a static version of the site from anywhere while still connecting to your Replit backend.

## Suite Features

The Discord Tools Suite includes 12 powerful tools for enhancing your Discord experience:

1. **Discord Typing Indicator**: Send continuous typing indicators to make your presence known
2. **Discord Status Changer**: Automatically cycle through customized status messages
3. **Discord Message Scheduler**: Schedule messages to be sent at specific times
4. **Discord Voice Joiner**: Automatically join voice channels to maintain presence
5. **Discord Auto-Reactor**: Add reactions to messages automatically based on content
6. **Discord User Tracker**: Monitor when specific users come online or go offline
7. **Discord Server Scanner**: Analyze server activity and member engagement
8. **Discord Channel Monitor**: Get notified of new messages in specific channels
9. **Discord DM Assistant**: Auto-respond to direct messages when you're away
10. **Discord Mention Watcher**: Get alerts when you're mentioned in any channel
11. **Discord Activity Simulator**: Simulate various activities to maintain online status
12. **Discord Chat Logger**: Archive and save chat conversations automatically

## Core System Features

- **Dual Operation Modes**:
  - **Discord Bot Mode**: Uses the official Discord Bot API (recommended)
  - **User Token Mode**: Uses a user account token (use at your own risk)
- **Anti-Detection Measures**: Random intervals and breaks to avoid detection
- **Auto-Recovery**: Watchdog system that monitors and restarts tools if they crash
- **Web Dashboard**: Control and monitor all tools via an intuitive web interface
- **Secure Credential Management**: Upload credentials via file or direct entry
- **Advanced Configuration**: Customize each tool's behavior via the dashboard
- **Detailed Logging**: Comprehensive logging for monitoring and debugging
- **GitHub Pages Compatibility**: Run a static version of the site that connects to your Replit backend

## Setup

1. Clone this repository
2. Run the application with `python main.py` or `gunicorn main:app`
3. Open the web dashboard at `http://localhost:5000`
4. Register an account and verify your email
5. Set up your Discord credentials using one of the two methods:
   - Upload a credentials file
   - Enter your credentials directly in the web UI

### Using the File Upload Feature

1. Create a plain text file (.txt) with your Discord credentials:
```
BOT_TOKEN=your_bot_token_here
CHANNEL_ID=your_channel_id_here
```
   
   Or for user token mode:
```
USER_TOKEN=your_user_token_here
CHANNEL_ID=your_channel_id_here
```

2. Upload this file through the web dashboard
3. Start the desired tool using the dashboard controls

### Discord Bot Setup

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application and add a bot
3. Enable the necessary intents (Message Content, Presence, Server Members)
4. Copy your bot token to use in the credentials upload
5. Invite the bot to your server with the proper permissions
6. Get the channel ID by enabling Developer Mode in Discord and right-clicking on a channel

## Web Dashboard

The suite includes a comprehensive web dashboard that allows you to:

- Start, stop, and monitor all tools
- Configure advanced settings for each tool
- Securely manage Discord credentials
- View detailed logs and statistics
- Maintain tools running even when you leave the site

The dashboard is available at `http://localhost:5000` by default.

## GitHub Pages Support

This project now includes support for GitHub Pages, allowing you to:

1. Host a static version of the site on GitHub Pages
2. Connect to your Replit backend from the GitHub Pages site
3. Provide a public showcase of your tools while keeping the backend secure

### Setting up GitHub Pages

1. Fork this repository to your GitHub account
2. Update the `docs/js/config.js` file with your Replit URL
3. Enable GitHub Pages in your repository settings, using the `/docs` folder
4. Your site will be available at `https://yourusername.github.io/DiscordTools/`
5. The GitHub Pages site will automatically connect to your Replit backend for dynamic features

For detailed instructions, see the [GitHub Pages README](docs/README.md).

## Anti-Detection Features

The Discord Tools Suite includes advanced anti-detection measures:

- Random typing intervals to simulate human behavior
- Randomized breaks to avoid pattern detection
- Configurable chance of taking longer breaks
- Minimum and maximum interval/break durations

## Security Notice

All credential information is processed locally on your machine and never stored in our database. Discord tokens are kept only in memory for the duration of your session for maximum security.

## Warning

Using a user token instead of a bot token may violate Discord's Terms of Service and could lead to your account being banned. We are not responsible for any account actions taken by Discord. Use these tools at your own risk and always comply with Discord's Terms of Service.

## License

MIT License
