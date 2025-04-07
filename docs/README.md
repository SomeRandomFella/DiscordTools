# Discord Tools Suite - GitHub Pages Version

This directory contains the GitHub Pages version of the Discord Tools Suite, which provides a static site that can interact with the main application backend.

## How It Works

The GitHub Pages site is a static website that includes:

1. HTML pages for the user interface
2. CSS styles and animations
3. JavaScript for dynamic content and interactions
4. Assets like SVG icons and images

The site connects to your deployed Discord Tools Suite backend API to fetch data and perform operations. It's designed to work in two modes:

### Connected Mode
When your Replit backend is running and accessible, the GitHub Pages site will fetch real data from your API endpoints:
- `/api/tools` - Gets the list of available tools
- `/api/online-count` - Gets the current number of online users

### Fallback Mode
If the connection to your backend fails or is unavailable, the site will fall back to displaying static content with links to your Replit deployment.

## Setup Instructions

### 1. Update the Configuration

Edit the `js/config.js` file to set your actual Replit deployment URL:

```javascript
const CONFIG = {
    // Backend API URL - change this to your deployed Replit URL
    API_URL: 'https://discord-tools-suite.your-replit-username.repl.co',
    
    // GitHub Pages base URL - update with your actual GitHub username
    GITHUB_PAGES_URL: 'https://SomeRandomFella.github.io/DiscordTools',
    
    // Version info
    VERSION: '1.0.0',
    
    // Feature flags
    FEATURES: {
        ENABLE_ONLINE_COUNT: true,
        ENABLE_TOOL_PREVIEW: true
    }
};
```

### 2. Deploy to GitHub Pages

1. Push this directory to a GitHub repository
2. Enable GitHub Pages for the repository, using the `/docs` folder as the source
3. Your site will be available at `https://yourusername.github.io/your-repo-name/`

### 3. Ensure CORS is configured

The backend API needs to allow cross-origin requests from your GitHub Pages domain. This is already configured in the Flask application with the CORS decorator.

## Directory Structure

- `/css` - Stylesheet files
- `/js` - JavaScript files
- `/images` - SVG icons and other assets
- `index.html` - Home page
- `all_tools.html` - Page listing all available tools

## Customization

You can customize the look and feel by editing the CSS files, or add new features by modifying the JavaScript files. The main files to focus on are:

- `css/styles.css` - Main stylesheet
- `js/app.js` - Core application logic
- `js/all-tools.js` - Code for the All Tools page
- `js/config.js` - Configuration file

## Security Considerations

- The GitHub Pages site does not store any user credentials
- All sensitive operations redirect to the secure Replit backend
- No discord tokens or API keys are ever exposed on the client side

## Technical Notes

- The site uses Bootstrap 5 for responsive layout and components
- Custom animations make the UI more engaging
- SVG icons ensure sharp graphics at any screen size
- Progressive enhancement ensures basic functionality even without JavaScript