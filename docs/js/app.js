// Main JavaScript for Discord Tools Suite GitHub Pages

document.addEventListener('DOMContentLoaded', () => {
    // Initialize the application
    initApp();
    
    // Setup navigation and link handling
    setupNavigation();
    
    // Load dynamic content
    loadFeaturedTools();
    
    // Update UI elements
    updateUIElements();
});

// Initialize the application
function initApp() {
    console.log('Discord Tools Suite initialized');
    
    // Add scroll event listener for navbar
    window.addEventListener('scroll', () => {
        const navbar = document.querySelector('.navbar');
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
    
    // Add loading bar functionality for page transitions
    const loadingBar = document.getElementById('loadingBar');
    if (loadingBar) {
        // Simulate loading for demo purposes
        loadingBar.style.width = '70%';
        setTimeout(() => {
            loadingBar.style.width = '100%';
            setTimeout(() => {
                loadingBar.style.width = '0%';
            }, 400);
        }, 300);
    }
}

// Setup navigation and link handling
function setupNavigation() {
    const apiUrl = window.DISCORD_TOOLS_CONFIG.API_URL;
    
    // Update app link
    const appLink = document.getElementById('appLink');
    if (appLink) {
        appLink.href = apiUrl;
    }
    
    // Update dashboard link
    const dashboardLink = document.getElementById('dashboardLink');
    if (dashboardLink) {
        dashboardLink.href = `${apiUrl}/dashboard`;
    }
    
    // Update login link
    const loginLink = document.getElementById('loginLink');
    if (loginLink) {
        loginLink.href = `${apiUrl}/login`;
    }
    
    // Update get started link
    const getStartedLink = document.getElementById('getStartedLink');
    if (getStartedLink) {
        getStartedLink.href = `${apiUrl}/register`;
    }
}

// Sample tools data (this would typically come from an API in a real app)
const toolsData = [
    {
        name: "Typing Indicator",
        description: "Keep your status as 'typing...' indefinitely in any Discord channel.",
        icon: "images/typing-icon.svg",
        url: "https://discord-tools-suite.your-replit-username.repl.co/tool/typing"
    },
    {
        name: "Status Monitor",
        description: "Monitor Discord status and receive alerts when services go down.",
        icon: "images/status-icon.svg",
        url: "https://discord-tools-suite.your-replit-username.repl.co/tool/status"
    },
    {
        name: "Message Scheduler",
        description: "Schedule messages to be sent at specific times in any channel.",
        icon: "images/message-icon.svg",
        url: "https://discord-tools-suite.your-replit-username.repl.co/tool/scheduler"
    },
    {
        name: "Reactions Manager",
        description: "Automatically add reactions to messages in selected channels.",
        icon: "images/reaction-icon.svg",
        url: "https://discord-tools-suite.your-replit-username.repl.co/tool/reactions"
    }
];

// Load featured tools
function loadFeaturedTools() {
    const featuredToolsContainer = document.getElementById('featuredTools');
    if (!featuredToolsContainer) return;
    
    // Clear container
    featuredToolsContainer.innerHTML = '';
    
    // Show loading state
    featuredToolsContainer.innerHTML = `
        <div class="col-12 text-center py-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="text-white mt-3">Loading tools...</p>
        </div>
    `;
    
    // Fetch tools from the API
    const apiUrl = window.DISCORD_TOOLS_CONFIG.API_URL;
    
    fetch(`${apiUrl}/api/tools?featured=true`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Clear loading state
            featuredToolsContainer.innerHTML = '';
            
            // Check if we got tools
            if (!data.tools || data.tools.length === 0) {
                featuredToolsContainer.innerHTML = `
                    <div class="col-12 text-center py-5">
                        <p class="text-white">No tools available</p>
                    </div>
                `;
                return;
            }
            
            // Add tools to container
            data.tools.forEach((tool, index) => {
                const toolElement = document.createElement('div');
                toolElement.className = 'col-md-6 col-lg-3 stagger-item';
                toolElement.innerHTML = `
                    <div class="card h-100 shadow-sm text-center">
                        <div class="card-body d-flex flex-column">
                            <img src="images/${tool.icon}" alt="${tool.name}" class="tool-icon mx-auto">
                            <h5 class="card-title text-white">${tool.name}</h5>
                            <p class="card-text flex-grow-1 text-white">${tool.description}</p>
                            <a href="${tool.url}" class="btn btn-sm btn-primary mt-3">Get Started</a>
                        </div>
                    </div>
                `;
                
                featuredToolsContainer.appendChild(toolElement);
                
                // Add staggered animation effect
                setTimeout(() => {
                    toolElement.classList.add('animate__animated', 'animate__fadeInUp');
                    toolElement.style.opacity = 1;
                }, 100 * index);
            });
        })
        .catch(error => {
            console.error('Error fetching tools:', error);
            
            // Show error state
            featuredToolsContainer.innerHTML = `
                <div class="col-12 text-center py-5">
                    <div class="alert alert-danger">
                        <p class="mb-0">Error loading tools. Either the server is down or you're viewing the static GitHub Pages version without a running backend.</p>
                        <p class="mb-0 mt-2">Using fallback data...</p>
                    </div>
                </div>
            `;
            
            // Use fallback data
            setTimeout(() => {
                featuredToolsContainer.innerHTML = '';
                
                // Add tools to container from static data
                toolsData.forEach((tool, index) => {
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
                    
                    featuredToolsContainer.appendChild(toolElement);
                    
                    // Add staggered animation effect
                    setTimeout(() => {
                        toolElement.classList.add('animate__animated', 'animate__fadeInUp');
                        toolElement.style.opacity = 1;
                    }, 100 * index);
                });
            }, 1500);
        });
}

// Update UI elements with dynamic data
function updateUIElements() {
    // Update online count (this would typically come from an API)
    const onlineCountElement = document.getElementById('onlineCount');
    if (onlineCountElement) {
        // Simulate online count for GitHub Pages
        const randomOnlineCount = Math.floor(Math.random() * 50) + 10;
        onlineCountElement.textContent = randomOnlineCount;
        
        // In a real implementation, this would fetch from the API:
        /*
        fetch(`${window.DISCORD_TOOLS_CONFIG.API_URL}/api/online-count`)
            .then(response => response.json())
            .then(data => {
                onlineCountElement.textContent = data.count;
            })
            .catch(error => {
                console.error('Error fetching online count:', error);
                onlineCountElement.textContent = '--';
            });
        */
    }
}