// JavaScript for All Tools page

document.addEventListener('DOMContentLoaded', () => {
    // Load all tools
    loadAllTools();
});

// Full list of tools (this would typically come from an API in a real app)
const allToolsData = [
    {
        name: "Typing Indicator",
        description: "Keep your status as 'typing...' indefinitely in any Discord channel.",
        icon: "images/typing-icon.svg",
        url: "https://discord-tools-suite.your-replit-username.repl.co/tool/typing",
        category: "presence"
    },
    {
        name: "Status Monitor",
        description: "Monitor Discord status and receive alerts when services go down.",
        icon: "images/status-icon.svg",
        url: "https://discord-tools-suite.your-replit-username.repl.co/tool/status",
        category: "monitoring"
    },
    {
        name: "Message Scheduler",
        description: "Schedule messages to be sent at specific times in any channel.",
        icon: "images/message-icon.svg",
        url: "https://discord-tools-suite.your-replit-username.repl.co/tool/scheduler",
        category: "messaging"
    },
    {
        name: "Reactions Manager",
        description: "Automatically add reactions to messages in selected channels.",
        icon: "images/reaction-icon.svg",
        url: "https://discord-tools-suite.your-replit-username.repl.co/tool/reactions",
        category: "interactions"
    },
    {
        name: "Voice Activity",
        description: "Maintain voice activity status without being in a voice channel.",
        icon: "images/voice-icon.svg",
        url: "https://discord-tools-suite.your-replit-username.repl.co/tool/voice",
        category: "presence"
    },
    {
        name: "Server Monitor",
        description: "Get notifications when users join or leave servers.",
        icon: "images/monitor-icon.svg",
        url: "https://discord-tools-suite.your-replit-username.repl.co/tool/server",
        category: "monitoring"
    },
    {
        name: "Auto Responder",
        description: "Create automated responses to specific message triggers.",
        icon: "images/message-icon.svg",
        url: "https://discord-tools-suite.your-replit-username.repl.co/tool/responder",
        category: "messaging"
    },
    {
        name: "Chat Activity",
        description: "Simulate chat activity during specified hours.",
        icon: "images/typing-icon.svg",
        url: "https://discord-tools-suite.your-replit-username.repl.co/tool/chatactivity",
        category: "presence"
    }
];

// Load all tools into the page
function loadAllTools() {
    const allToolsContainer = document.getElementById('allToolsContainer');
    if (!allToolsContainer) return;
    
    // Clear container
    allToolsContainer.innerHTML = '';
    
    // Update API URLs in tool data
    const apiUrl = window.DISCORD_TOOLS_CONFIG.API_URL;
    const updatedToolsData = allToolsData.map(tool => ({
        ...tool,
        url: tool.url.replace('https://discord-tools-suite.your-replit-username.repl.co', apiUrl)
    }));
    
    // Group tools by category
    const toolsByCategory = groupByCategory(updatedToolsData);
    
    // Loop through categories
    Object.keys(toolsByCategory).forEach(category => {
        // Create category header
        const categoryHeader = document.createElement('div');
        categoryHeader.className = 'col-12 mb-3 mt-4';
        categoryHeader.innerHTML = `
            <h3 class="text-white">${formatCategoryName(category)}</h3>
            <hr class="border-secondary">
        `;
        allToolsContainer.appendChild(categoryHeader);
        
        // Add tools for this category
        toolsByCategory[category].forEach((tool, index) => {
            const toolElement = document.createElement('div');
            toolElement.className = 'col-md-6 col-lg-3 stagger-item';
            toolElement.innerHTML = `
                <div class="card h-100 shadow-sm text-center">
                    <div class="card-body d-flex flex-column">
                        <img src="${tool.icon}" alt="${tool.name}" class="tool-icon mx-auto">
                        <h5 class="card-title text-white">${tool.name}</h5>
                        <p class="card-text flex-grow-1 text-white">${tool.description}</p>
                        <a href="${tool.url}" class="btn btn-sm btn-primary mt-3">Get Started</a>
                    </div>
                </div>
            `;
            
            allToolsContainer.appendChild(toolElement);
            
            // Add staggered animation effect
            setTimeout(() => {
                toolElement.classList.add('animate__animated', 'animate__fadeInUp');
                toolElement.style.opacity = 1;
            }, 100 * index);
        });
    });
}

// Helper function to group tools by category
function groupByCategory(tools) {
    return tools.reduce((groups, tool) => {
        const category = tool.category || 'other';
        if (!groups[category]) {
            groups[category] = [];
        }
        groups[category].push(tool);
        return groups;
    }, {});
}

// Helper function to format category name
function formatCategoryName(category) {
    const formatted = category.charAt(0).toUpperCase() + category.slice(1);
    
    switch(category) {
        case 'presence':
            return '👀 ' + formatted + ' Tools';
        case 'messaging':
            return '💬 ' + formatted + ' Tools';
        case 'monitoring':
            return '📊 ' + formatted + ' Tools';
        case 'interactions':
            return '🔄 ' + formatted + ' Tools';
        default:
            return '🛠️ ' + formatted + ' Tools';
    }
}