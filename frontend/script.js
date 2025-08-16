// API base URL - use relative path to work from any host
const API_URL = '/api';

// Global state
let currentSessionId = null;

// DOM elements
let chatMessages, chatInput, sendButton, totalCourses, courseTitles;

// Visualization state
let currentVisualization = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Get DOM elements after page loads
    chatMessages = document.getElementById('chatMessages');
    chatInput = document.getElementById('chatInput');
    sendButton = document.getElementById('sendButton');
    totalCourses = document.getElementById('totalCourses');
    courseTitles = document.getElementById('courseTitles');
    
    setupEventListeners();
    createNewSession();
    loadCourseStats();
});

// Event Listeners
function setupEventListeners() {
    // Chat functionality
    sendButton.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
    
    // Tab switching
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const tabName = e.target.getAttribute('data-tab');
            switchTab(tabName);
        });
    });
    
    // Visualization controls
    const refreshBtn = document.getElementById('refreshViz');
    const centerBtn = document.getElementById('centerViz');
    const vizModeSelect = document.getElementById('vizMode');
    
    if (refreshBtn) refreshBtn.addEventListener('click', refreshVisualization);
    if (centerBtn) centerBtn.addEventListener('click', centerVisualization);
    if (vizModeSelect) vizModeSelect.addEventListener('change', changeVisualizationMode);
    
    // Suggested questions
    document.querySelectorAll('.suggested-item').forEach(button => {
        button.addEventListener('click', (e) => {
            const question = e.target.getAttribute('data-question');
            chatInput.value = question;
            sendMessage();
        });
    });
}


// Chat Functions
async function sendMessage() {
    const query = chatInput.value.trim();
    if (!query) return;

    // Disable input
    chatInput.value = '';
    chatInput.disabled = true;
    sendButton.disabled = true;

    // Add user message
    addMessage(query, 'user');

    // Add loading message - create a unique container for it
    const loadingMessage = createLoadingMessage();
    chatMessages.appendChild(loadingMessage);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    try {
        const response = await fetch(`${API_URL}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                session_id: currentSessionId
            })
        });

        if (!response.ok) throw new Error('Query failed');

        const data = await response.json();
        
        // Update session ID if new
        if (!currentSessionId) {
            currentSessionId = data.session_id;
        }

        // Replace loading message with response
        loadingMessage.remove();
        addMessage(data.answer, 'assistant', data.sources);

    } catch (error) {
        // Replace loading message with error
        loadingMessage.remove();
        addMessage(`Error: ${error.message}`, 'assistant');
    } finally {
        chatInput.disabled = false;
        sendButton.disabled = false;
        chatInput.focus();
    }
}

function createLoadingMessage() {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';
    messageDiv.innerHTML = `
        <div class="message-content">
            <div class="loading">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;
    return messageDiv;
}

function addMessage(content, type, sources = null, isWelcome = false) {
    const messageId = Date.now();
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}${isWelcome ? ' welcome-message' : ''}`;
    messageDiv.id = `message-${messageId}`;
    
    // Convert markdown to HTML for assistant messages
    const displayContent = type === 'assistant' ? marked.parse(content) : escapeHtml(content);
    
    let html = `<div class="message-content">${displayContent}</div>`;
    
    if (sources && sources.length > 0) {
        html += `
            <details class="sources-collapsible">
                <summary class="sources-header">Sources</summary>
                <div class="sources-content">${sources.join(', ')}</div>
            </details>
        `;
    }
    
    messageDiv.innerHTML = html;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    return messageId;
}

// Helper function to escape HTML for user messages
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Removed removeMessage function - no longer needed since we handle loading differently

async function createNewSession() {
    currentSessionId = null;
    chatMessages.innerHTML = '';
    addMessage('Welcome to the Course Materials Assistant! I can help you with questions about courses, lessons and specific content. What would you like to know?', 'assistant', null, true);
}

// Load course statistics
async function loadCourseStats() {
    try {
        console.log('Loading course stats...');
        const response = await fetch(`${API_URL}/courses`);
        if (!response.ok) throw new Error('Failed to load course stats');
        
        const data = await response.json();
        console.log('Course data received:', data);
        
        // Update stats in UI
        if (totalCourses) {
            totalCourses.textContent = data.total_courses;
        }
        
        // Update course titles
        if (courseTitles) {
            if (data.course_titles && data.course_titles.length > 0) {
                courseTitles.innerHTML = data.course_titles
                    .map(title => `<div class="course-title-item">${title}</div>`)
                    .join('');
            } else {
                courseTitles.innerHTML = '<span class="no-courses">No courses available</span>';
            }
        }
        
    } catch (error) {
        console.error('Error loading course stats:', error);
        // Set default values on error
        if (totalCourses) {
            totalCourses.textContent = '0';
        }
        if (courseTitles) {
            courseTitles.innerHTML = '<span class="error">Failed to load courses</span>';
        }
    }
}

// Tab Management
function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    
    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`${tabName}-tab`).classList.add('active');
    
    // Load visualization if switching to visualization tab
    if (tabName === 'visualization' && !currentVisualization) {
        loadVisualization();
    }
}

// Visualization Functions
async function loadVisualization() {
    const container = document.getElementById('courseVisualization');
    if (!container) return;
    
    container.innerHTML = '<div class="viz-loading">Loading visualization...</div>';
    
    try {
        const response = await fetch(`${API_URL}/visualization-data`);
        if (!response.ok) throw new Error('Failed to load visualization data');
        
        const data = await response.json();
        createNetworkVisualization(data);
        
    } catch (error) {
        console.error('Error loading visualization:', error);
        container.innerHTML = '<div class="viz-error">Failed to load visualization. Please try again.</div>';
    }
}

function createNetworkVisualization(data) {
    const container = document.getElementById('courseVisualization');
    container.innerHTML = ''; // Clear loading message
    
    const width = container.clientWidth;
    const height = container.clientHeight;
    
    // Create SVG
    const svg = d3.select(container)
        .append('svg')
        .attr('width', width)
        .attr('height', height)
        .style('background', 'var(--background)');
    
    // Create tooltip
    const tooltip = d3.select('body')
        .append('div')
        .attr('class', 'tooltip')
        .style('opacity', 0);
    
    // Setup force simulation
    const simulation = d3.forceSimulation(data.nodes)
        .force('link', d3.forceLink(data.links).id(d => d.id).distance(80))
        .force('charge', d3.forceManyBody().strength(-300))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide().radius(25));
    
    // Create links
    const link = svg.append('g')
        .attr('class', 'links')
        .selectAll('line')
        .data(data.links)
        .enter().append('line')
        .attr('class', 'link')
        .style('stroke', '#475569')
        .style('stroke-opacity', 0.6)
        .style('stroke-width', 2);
    
    // Create nodes
    const node = svg.append('g')
        .attr('class', 'nodes')
        .selectAll('circle')
        .data(data.nodes)
        .enter().append('circle')
        .attr('class', d => `node ${d.type}`)
        .attr('r', d => {
            switch(d.type) {
                case 'instructor': return 20;
                case 'course': return 15;
                case 'lesson': return 10;
                default: return 10;
            }
        })
        .style('fill', d => {
            switch(d.type) {
                case 'instructor': return '#f59e0b';
                case 'course': return '#3b82f6';
                case 'lesson': return '#10b981';
                default: return '#6b7280';
            }
        })
        .style('stroke', d => {
            switch(d.type) {
                case 'instructor': return '#d97706';
                case 'course': return '#1d4ed8';
                case 'lesson': return '#047857';
                default: return '#374151';
            }
        })
        .style('stroke-width', 2)
        .style('cursor', 'pointer')
        .call(d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended));
    
    // Add labels
    const label = svg.append('g')
        .attr('class', 'labels')
        .selectAll('text')
        .data(data.nodes)
        .enter().append('text')
        .attr('class', 'node-label')
        .text(d => {
            // Truncate long names
            return d.name.length > 20 ? d.name.substring(0, 17) + '...' : d.name;
        })
        .style('font-size', '11px')
        .style('fill', '#f1f5f9')
        .style('text-anchor', 'middle')
        .style('pointer-events', 'none')
        .style('text-shadow', '-1px -1px 0 #0f172a, 1px -1px 0 #0f172a, -1px 1px 0 #0f172a, 1px 1px 0 #0f172a');
    
    // Tooltip events
    node.on('mouseover', function(event, d) {
        let tooltipContent = `<div class="tooltip-title">${d.name}</div>`;
        
        switch(d.type) {
            case 'instructor':
                tooltipContent += `<div class="tooltip-info">Instructor</div>`;
                break;
            case 'course':
                tooltipContent += `<div class="tooltip-info">Course by ${d.instructor}<br/>Lessons: ${d.lesson_count}</div>`;
                break;
            case 'lesson':
                tooltipContent += `<div class="tooltip-info">Lesson ${d.lesson_number}<br/>Course: ${d.course}</div>`;
                break;
        }
        
        tooltip.transition().duration(200).style('opacity', .9);
        tooltip.html(tooltipContent)
            .style('left', (event.pageX + 10) + 'px')
            .style('top', (event.pageY - 28) + 'px');
    })
    .on('mouseout', function() {
        tooltip.transition().duration(500).style('opacity', 0);
    });
    
    // Click events for external links
    node.on('click', function(event, d) {
        if (d.course_link) {
            window.open(d.course_link, '_blank');
        } else if (d.lesson_link) {
            window.open(d.lesson_link, '_blank');
        }
    });
    
    // Update positions on simulation tick
    simulation.on('tick', () => {
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);
        
        node
            .attr('cx', d => d.x)
            .attr('cy', d => d.y);
        
        label
            .attr('x', d => d.x)
            .attr('y', d => d.y + 4);
    });
    
    // Drag functions
    function dragstarted(event) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
    }
    
    function dragged(event) {
        event.subject.fx = event.x;
        event.subject.fy = event.y;
    }
    
    function dragended(event) {
        if (!event.active) simulation.alphaTarget(0);
        event.subject.fx = null;
        event.subject.fy = null;
    }
    
    // Store visualization for controls
    currentVisualization = {
        svg: svg,
        simulation: simulation,
        tooltip: tooltip,
        width: width,
        height: height
    };
}

// Visualization Controls
function refreshVisualization() {
    if (currentVisualization) {
        currentVisualization.tooltip.remove();
        currentVisualization = null;
    }
    loadVisualization();
}

function centerVisualization() {
    if (currentVisualization) {
        currentVisualization.simulation
            .force('center', d3.forceCenter(currentVisualization.width / 2, currentVisualization.height / 2))
            .alpha(0.3)
            .restart();
    }
}

function changeVisualizationMode() {
    const mode = document.getElementById('vizMode').value;
    if (!currentVisualization) return;
    
    // Clear current forces and restart with new layout
    const { simulation, width, height } = currentVisualization;
    
    switch(mode) {
        case 'radial':
            simulation
                .force('charge', d3.forceManyBody().strength(-200))
                .force('radial', d3.forceRadial(100, width / 2, height / 2).strength(0.1))
                .alpha(0.3)
                .restart();
            break;
        case 'tree':
            simulation
                .force('charge', d3.forceManyBody().strength(-100))
                .force('y', d3.forceY(d => d.group * 150 + 100).strength(0.5))
                .force('x', d3.forceX(width / 2).strength(0.1))
                .alpha(0.3)
                .restart();
            break;
        default: // network
            simulation
                .force('charge', d3.forceManyBody().strength(-300))
                .force('radial', null)
                .force('y', null)
                .force('x', null)
                .alpha(0.3)
                .restart();
            break;
    }
}