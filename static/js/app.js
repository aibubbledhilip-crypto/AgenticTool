/**
 * DVSum Agentic AI Automation - Frontend Application
 */

// ==================== State Management ====================

const state = {
    configured: false,
    currentSection: 'chat',
    agents: [],
    workflows: [],
    dataSources: [],
    chatMessages: [],
    history: []
};

// ==================== API Client ====================

const api = {
    baseUrl: '',

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json'
            }
        };

        try {
            const response = await fetch(url, { ...defaultOptions, ...options });
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('API Error:', error);
            return { success: false, error: error.message };
        }
    },

    // Configuration
    async getConfig() {
        return this.request('/api/config');
    },

    async setConfig(config) {
        return this.request('/api/config', {
            method: 'POST',
            body: JSON.stringify(config)
        });
    },

    async testConnection() {
        return this.request('/api/test-connection', { method: 'POST' });
    },

    // Agentic AI
    async processMessage(message) {
        return this.request('/api/agentic/process', {
            method: 'POST',
            body: JSON.stringify({ message })
        });
    },

    async getHistory() {
        return this.request('/api/agentic/history');
    },

    async clearHistory() {
        return this.request('/api/agentic/clear', { method: 'POST' });
    },

    // Agents
    async listAgents() {
        return this.request('/api/agents');
    },

    async createAgent(config) {
        return this.request('/api/agents', {
            method: 'POST',
            body: JSON.stringify(config)
        });
    },

    async executeAgent(agentId, input, context) {
        return this.request(`/api/agents/${agentId}/execute`, {
            method: 'POST',
            body: JSON.stringify({ input, context })
        });
    },

    async chatWithAgent(agentId, message, conversationId) {
        return this.request(`/api/agents/${agentId}/chat`, {
            method: 'POST',
            body: JSON.stringify({ message, conversation_id: conversationId })
        });
    },

    // Workflows
    async listWorkflows() {
        return this.request('/api/workflows');
    },

    async createWorkflow(config) {
        return this.request('/api/workflows', {
            method: 'POST',
            body: JSON.stringify(config)
        });
    },

    async executeWorkflow(workflowId, input) {
        return this.request(`/api/workflows/${workflowId}/execute`, {
            method: 'POST',
            body: JSON.stringify(input)
        });
    },

    // Data Sources
    async listDataSources() {
        return this.request('/api/datasources');
    },

    async connectDataSource(config) {
        return this.request('/api/datasources', {
            method: 'POST',
            body: JSON.stringify(config)
        });
    },

    // Data Quality
    async runDQCheck(dataSourceId, rules) {
        return this.request('/api/dataquality/check', {
            method: 'POST',
            body: JSON.stringify({ data_source_id: dataSourceId, rules })
        });
    },

    async getDQExceptions(dataSourceId) {
        const params = dataSourceId ? `?data_source_id=${dataSourceId}` : '';
        return this.request(`/api/dataquality/exceptions${params}`);
    },

    // Health
    async healthCheck() {
        return this.request('/api/health');
    }
};

// ==================== UI Functions ====================

function showSection(sectionName) {
    // Update navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
        if (item.dataset.section === sectionName) {
            item.classList.add('active');
        }
    });

    // Update sections
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });
    document.getElementById(`section-${sectionName}`).classList.add('active');

    // Update title
    const titles = {
        chat: 'Agentic AI Chat',
        agents: 'AI Agents',
        workflows: 'Automation Workflows',
        datasources: 'Data Sources',
        dataquality: 'Data Quality',
        history: 'Execution History',
        settings: 'Settings'
    };
    document.getElementById('page-title').textContent = titles[sectionName] || sectionName;

    state.currentSection = sectionName;

    // Load section data
    loadSectionData(sectionName);
}

async function loadSectionData(section) {
    switch (section) {
        case 'agents':
            await loadAgents();
            break;
        case 'workflows':
            await loadWorkflows();
            break;
        case 'datasources':
            await loadDataSources();
            break;
        case 'dataquality':
            await loadDQData();
            break;
        case 'history':
            await loadHistory();
            break;
    }
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<div class="toast-message">${message}</div>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'toastSlideIn 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

function updateConnectionStatus(connected) {
    const statusEl = document.getElementById('connection-status');
    const dot = statusEl.querySelector('.status-dot');
    const text = statusEl.querySelector('.status-text');

    if (connected) {
        dot.classList.add('connected');
        text.textContent = 'Connected';
    } else {
        dot.classList.remove('connected');
        text.textContent = 'Not Connected';
    }
    state.configured = connected;
}

// ==================== Chat Functions ====================

function addMessage(content, isUser = false, details = null) {
    const messagesContainer = document.getElementById('chat-messages');

    // Remove welcome message if exists
    const welcomeMsg = messagesContainer.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }

    const message = document.createElement('div');
    message.className = `message ${isUser ? 'user' : 'assistant'}`;

    let detailsHTML = '';
    if (details) {
        if (details.actions_taken && details.actions_taken.length > 0) {
            detailsHTML += `
                <div class="message-actions">
                    <h4>Actions Taken</h4>
                    <div class="action-list">
                        ${details.actions_taken.map(a => `<div class="action-item">${a}</div>`).join('')}
                    </div>
                </div>
            `;
        }
        if (details.recommendations && details.recommendations.length > 0) {
            detailsHTML += `
                <div class="recommendations">
                    <h4>Recommendations</h4>
                    ${details.recommendations.map(r => `<div class="recommendation-item">${r}</div>`).join('')}
                </div>
            `;
        }
    }

    message.innerHTML = `
        <div class="message-avatar">${isUser ? '&#128100;' : '&#9670;'}</div>
        <div class="message-content">
            <div class="message-text">${content}</div>
            ${details ? `<div class="message-details">Task: ${details.task_type || 'custom'}</div>` : ''}
            ${detailsHTML}
        </div>
    `;

    messagesContainer.appendChild(message);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

async function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();

    if (!message) return;

    // Add user message
    addMessage(message, true);
    input.value = '';
    input.style.height = 'auto';

    // Show loading
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message assistant';
    loadingDiv.id = 'loading-message';
    loadingDiv.innerHTML = `
        <div class="message-avatar">&#9670;</div>
        <div class="message-content">
            <div class="loading-spinner"></div>
            <div class="message-text">Processing your request...</div>
        </div>
    `;
    document.getElementById('chat-messages').appendChild(loadingDiv);

    // Send to API
    const response = await api.processMessage(message);

    // Remove loading
    document.getElementById('loading-message')?.remove();

    // Add response
    if (response.success) {
        let responseText = 'Task completed successfully.';

        if (response.result) {
            if (typeof response.result === 'string') {
                responseText = response.result;
            } else if (response.result.message) {
                responseText = response.result.message;
            } else if (response.result.summary) {
                responseText = response.result.summary;
            } else {
                responseText = `Processed ${response.task_type} request successfully.`;
            }
        }

        addMessage(responseText, false, {
            task_type: response.task_type,
            actions_taken: response.actions_taken,
            recommendations: response.recommendations
        });
    } else {
        addMessage(`Error: ${response.error || 'Unknown error occurred'}`, false);
    }
}

function insertSuggestion(text) {
    const input = document.getElementById('chat-input');
    input.value = text;
    input.focus();
}

// ==================== Agents Functions ====================

async function loadAgents() {
    const grid = document.getElementById('agents-grid');
    grid.innerHTML = '<div class="loading-placeholder"><div class="loading-spinner"></div>Loading agents...</div>';

    const response = await api.listAgents();

    if (response.success && response.data) {
        const agents = response.data;
        if (agents.length === 0) {
            grid.innerHTML = '<div class="no-data">No agents configured yet. Create your first agent!</div>';
        } else {
            grid.innerHTML = agents.map(agent => `
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">${agent.name || 'Unnamed Agent'}</div>
                        <span class="card-badge ${agent.status || 'active'}">${agent.status || 'Active'}</span>
                    </div>
                    <div class="card-description">${agent.description || 'No description'}</div>
                    <div class="card-actions">
                        <button class="card-btn" onclick="viewAgent('${agent.id}')">View</button>
                        <button class="card-btn primary" onclick="executeAgentUI('${agent.id}')">Execute</button>
                    </div>
                </div>
            `).join('');
        }
    } else {
        grid.innerHTML = `<div class="no-data">Failed to load agents: ${response.error || 'Unknown error'}</div>`;
    }
}

async function createAgent() {
    const name = document.getElementById('agent-name').value;
    const type = document.getElementById('agent-type').value;
    const description = document.getElementById('agent-description').value;
    const rulesStr = document.getElementById('agent-rules').value;

    let rules = {};
    if (rulesStr) {
        try {
            rules = JSON.parse(rulesStr);
        } catch (e) {
            showToast('Invalid JSON in rules field', 'error');
            return;
        }
    }

    const response = await api.createAgent({ name, type, description, rules });

    if (response.success) {
        showToast('Agent created successfully', 'success');
        closeModal();
        loadAgents();
    } else {
        showToast(`Failed to create agent: ${response.error}`, 'error');
    }
}

async function executeAgentUI(agentId) {
    const input = prompt('Enter input for the agent (JSON format):');
    if (!input) return;

    try {
        const inputData = JSON.parse(input);
        const response = await api.executeAgent(agentId, inputData);

        if (response.success) {
            showToast('Agent executed successfully', 'success');
        } else {
            showToast(`Execution failed: ${response.error}`, 'error');
        }
    } catch (e) {
        showToast('Invalid JSON input', 'error');
    }
}

function viewAgent(agentId) {
    showToast(`Viewing agent ${agentId}`, 'info');
}

// ==================== Workflows Functions ====================

async function loadWorkflows() {
    const grid = document.getElementById('workflows-grid');
    grid.innerHTML = '<div class="loading-placeholder"><div class="loading-spinner"></div>Loading workflows...</div>';

    const response = await api.listWorkflows();

    if (response.success && response.data) {
        const workflows = response.data;
        if (workflows.length === 0) {
            grid.innerHTML = '<div class="no-data">No workflows configured yet. Create your first workflow!</div>';
        } else {
            grid.innerHTML = workflows.map(workflow => `
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">${workflow.name || 'Unnamed Workflow'}</div>
                        <span class="card-badge ${workflow.status || 'active'}">${workflow.trigger || 'Manual'}</span>
                    </div>
                    <div class="card-description">${workflow.description || 'No description'}</div>
                    <div class="card-actions">
                        <button class="card-btn" onclick="viewWorkflow('${workflow.id}')">View</button>
                        <button class="card-btn primary" onclick="executeWorkflowUI('${workflow.id}')">Run</button>
                    </div>
                </div>
            `).join('');
        }
    } else {
        grid.innerHTML = `<div class="no-data">Failed to load workflows: ${response.error || 'Unknown error'}</div>`;
    }
}

async function createWorkflow() {
    const name = document.getElementById('workflow-name').value;
    const trigger = document.getElementById('workflow-trigger').value;
    const stepsStr = document.getElementById('workflow-steps').value;

    let steps = [];
    if (stepsStr) {
        try {
            steps = JSON.parse(stepsStr);
        } catch (e) {
            showToast('Invalid JSON in steps field', 'error');
            return;
        }
    }

    const response = await api.createWorkflow({ name, trigger, steps });

    if (response.success) {
        showToast('Workflow created successfully', 'success');
        closeModal();
        loadWorkflows();
    } else {
        showToast(`Failed to create workflow: ${response.error}`, 'error');
    }
}

async function executeWorkflowUI(workflowId) {
    const response = await api.executeWorkflow(workflowId, {});

    if (response.success) {
        showToast('Workflow started successfully', 'success');
    } else {
        showToast(`Failed to start workflow: ${response.error}`, 'error');
    }
}

function viewWorkflow(workflowId) {
    showToast(`Viewing workflow ${workflowId}`, 'info');
}

// ==================== Data Sources Functions ====================

async function loadDataSources() {
    const grid = document.getElementById('datasources-grid');
    grid.innerHTML = '<div class="loading-placeholder"><div class="loading-spinner"></div>Loading data sources...</div>';

    const response = await api.listDataSources();

    if (response.success && response.data) {
        const sources = response.data;
        if (sources.length === 0) {
            grid.innerHTML = '<div class="no-data">No data sources connected yet. Connect your first data source!</div>';
        } else {
            grid.innerHTML = sources.map(source => `
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">${source.name || 'Unnamed Source'}</div>
                        <span class="card-badge ${source.status || 'active'}">${source.type || 'Unknown'}</span>
                    </div>
                    <div class="card-description">${source.description || source.connection || 'No description'}</div>
                    <div class="card-actions">
                        <button class="card-btn" onclick="viewDataSource('${source.id}')">View</button>
                        <button class="card-btn primary" onclick="queryDataSource('${source.id}')">Query</button>
                    </div>
                </div>
            `).join('');
        }
    } else {
        grid.innerHTML = `<div class="no-data">Failed to load data sources: ${response.error || 'Unknown error'}</div>`;
    }
}

async function connectDataSource() {
    const name = document.getElementById('datasource-name').value;
    const type = document.getElementById('datasource-type').value;
    const connection = document.getElementById('datasource-connection').value;

    const response = await api.connectDataSource({ name, type, connection });

    if (response.success) {
        showToast('Data source connected successfully', 'success');
        closeModal();
        loadDataSources();
    } else {
        showToast(`Failed to connect data source: ${response.error}`, 'error');
    }
}

function viewDataSource(sourceId) {
    showToast(`Viewing data source ${sourceId}`, 'info');
}

function queryDataSource(sourceId) {
    const query = prompt('Enter your natural language query:');
    if (query) {
        showSection('chat');
        insertSuggestion(query);
    }
}

// ==================== Data Quality Functions ====================

async function loadDQData() {
    const response = await api.getDQExceptions();

    if (response.success) {
        const exceptions = response.data || [];

        // Update stats
        document.getElementById('dq-total').textContent = exceptions.length;
        document.getElementById('dq-passed').textContent = exceptions.filter(e => e.severity === 'low').length;
        document.getElementById('dq-warnings').textContent = exceptions.filter(e => e.severity === 'medium').length;
        document.getElementById('dq-errors').textContent = exceptions.filter(e => e.severity === 'high').length;

        // Update exceptions list
        const listEl = document.getElementById('exceptions-list');
        if (exceptions.length === 0) {
            listEl.innerHTML = '<p class="no-data">No exceptions found</p>';
        } else {
            listEl.innerHTML = exceptions.map(exc => `
                <div class="exception-item">
                    <div class="exception-info">
                        <div class="exception-title">${exc.title || exc.rule || 'Exception'}</div>
                        <div class="exception-details">${exc.details || exc.message || ''}</div>
                    </div>
                    <span class="exception-severity ${exc.severity || 'medium'}">${exc.severity || 'Medium'}</span>
                </div>
            `).join('');
        }
    }
}

async function runDQCheck() {
    showToast('Running data quality check...', 'info');
    const response = await api.runDQCheck('all');

    if (response.success) {
        showToast('Data quality check completed', 'success');
        loadDQData();
    } else {
        showToast(`DQ check failed: ${response.error}`, 'error');
    }
}

// ==================== History Functions ====================

async function loadHistory() {
    const listEl = document.getElementById('history-list');
    listEl.innerHTML = '<div class="loading-placeholder"><div class="loading-spinner"></div>Loading history...</div>';

    const response = await api.getHistory();

    if (response.history && response.history.length > 0) {
        listEl.innerHTML = response.history.map((item, index) => `
            <div class="history-item">
                <div class="history-info">
                    <div class="history-task">${item.task || 'Unknown Task'}</div>
                    <div class="history-meta">
                        <span>Type: ${item.type || 'custom'}</span>
                        <span>Actions: ${(item.actions || []).length}</span>
                    </div>
                </div>
                <span class="history-status ${item.success ? 'success' : 'failed'}">
                    ${item.success ? 'Success' : 'Failed'}
                </span>
            </div>
        `).join('');
    } else {
        listEl.innerHTML = '<p class="no-data">No execution history yet</p>';
    }
}

async function clearHistory() {
    if (!confirm('Are you sure you want to clear all history?')) return;

    const response = await api.clearHistory();
    if (response.success) {
        showToast('History cleared', 'success');
        loadHistory();
    }
}

// ==================== Settings Functions ====================

async function loadSettings() {
    const response = await api.getConfig();

    if (response.configured) {
        updateConnectionStatus(true);
        if (response.base_url) {
            document.getElementById('api-base-url').value = response.base_url;
        }
    }
}

async function saveSettings() {
    const baseUrl = document.getElementById('api-base-url').value;
    const apiKey = document.getElementById('api-key').value;
    const tenantId = document.getElementById('tenant-id').value;

    if (!baseUrl || !apiKey) {
        showToast('Base URL and API Key are required', 'error');
        return;
    }

    const response = await api.setConfig({
        base_url: baseUrl,
        api_key: apiKey,
        tenant_id: tenantId || undefined
    });

    if (response.success) {
        showToast('Settings saved successfully', 'success');
        updateConnectionStatus(true);
    } else {
        showToast(`Failed to save settings: ${response.error}`, 'error');
    }
}

async function testConnection() {
    showToast('Testing connection...', 'info');
    const response = await api.testConnection();

    if (response.success) {
        showToast('Connection successful!', 'success');
        updateConnectionStatus(true);
    } else {
        showToast(`Connection failed: ${response.error}`, 'error');
        updateConnectionStatus(false);
    }
}

// ==================== Modal Functions ====================

function openModal(modalId) {
    document.getElementById('modal-overlay').classList.add('active');
    document.getElementById(modalId).classList.add('active');
}

function closeModal() {
    document.getElementById('modal-overlay').classList.remove('active');
    document.querySelectorAll('.modal').forEach(modal => {
        modal.classList.remove('active');
    });
}

// ==================== Event Listeners ====================

document.addEventListener('DOMContentLoaded', () => {
    // Navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const section = item.dataset.section;
            if (section) {
                showSection(section);
            }
        });
    });

    // Chat input
    const chatInput = document.getElementById('chat-input');
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Auto-resize textarea
    chatInput.addEventListener('input', () => {
        chatInput.style.height = 'auto';
        chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
    });

    // Send button
    document.getElementById('send-btn').addEventListener('click', sendMessage);

    // Clear button
    document.getElementById('clear-btn').addEventListener('click', () => {
        document.getElementById('chat-messages').innerHTML = `
            <div class="welcome-message">
                <h2>Welcome to DVSum Agentic AI</h2>
                <p>I can help you with:</p>
                <div class="capabilities-grid">
                    <div class="capability-card" onclick="insertSuggestion('Show me all available agents')">
                        <span class="capability-icon">&#129302;</span>
                        <span>List Agents</span>
                    </div>
                    <div class="capability-card" onclick="insertSuggestion('Analyze data quality issues')">
                        <span class="capability-icon">&#128202;</span>
                        <span>Analyze Data</span>
                    </div>
                    <div class="capability-card" onclick="insertSuggestion('Run a troubleshooting diagnostic')">
                        <span class="capability-icon">&#128295;</span>
                        <span>Troubleshoot</span>
                    </div>
                    <div class="capability-card" onclick="insertSuggestion('Create a summary report')">
                        <span class="capability-icon">&#128196;</span>
                        <span>Generate Reports</span>
                    </div>
                </div>
            </div>
        `;
        api.clearHistory();
    });

    // Modal overlay click
    document.getElementById('modal-overlay').addEventListener('click', (e) => {
        if (e.target.id === 'modal-overlay') {
            closeModal();
        }
    });

    // Load initial data
    loadSettings();
});

// Make functions available globally
window.insertSuggestion = insertSuggestion;
window.openModal = openModal;
window.closeModal = closeModal;
window.createAgent = createAgent;
window.viewAgent = viewAgent;
window.executeAgentUI = executeAgentUI;
window.createWorkflow = createWorkflow;
window.viewWorkflow = viewWorkflow;
window.executeWorkflowUI = executeWorkflowUI;
window.connectDataSource = connectDataSource;
window.viewDataSource = viewDataSource;
window.queryDataSource = queryDataSource;
window.runDQCheck = runDQCheck;
window.clearHistory = clearHistory;
window.saveSettings = saveSettings;
window.testConnection = testConnection;
