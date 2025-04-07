// Configuration for Discord Tools Suite
const CONFIG = {
    // Backend API URL - change this to your deployed Replit URL
    API_URL: 'https://discord-tools-suite.your-replit-username.repl.co',
    
    // GitHub Pages base URL - useful for absolute references
    GITHUB_PAGES_URL: 'https://SomeRandomFella.github.io/DiscordTools',
    
    // Version info
    VERSION: '1.0.0',
    
    // Feature flags
    FEATURES: {
        ENABLE_ONLINE_COUNT: true,
        ENABLE_TOOL_PREVIEW: true
    }
};

// Don't modify below this line
window.DISCORD_TOOLS_CONFIG = CONFIG;