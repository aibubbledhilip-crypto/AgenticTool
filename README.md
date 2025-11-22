# DVSum Agentic AI Automation Tool

A web-based GUI application for automating tasks using DVSum's Agentic AI platform. This tool provides an intuitive interface for interacting with DVSum APIs, managing AI agents, workflows, data sources, and data quality checks.

## Features

- **Agentic AI Chat**: Natural language interface to interact with DVSum's AI capabilities
- **Agent Management**: Create, view, and execute AI agents
- **Workflow Automation**: Design and run automated workflows
- **Data Source Integration**: Connect and query multiple data sources
- **Data Quality Monitoring**: Run DQ checks and view exceptions
- **Execution History**: Track all operations and their outcomes
- **Dashboard Management**: Create and manage dashboards with widgets
- **Asset Management**: Full CRUD operations on Terms, Tables, Columns, and more
- **Audit Trail**: Track all changes with comprehensive audit logging

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- DVSum OAuth2 credentials (Client ID and Client Secret)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd AgenticTool
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your DVSum API credentials
```

## Configuration

Edit the `.env` file with your DVSum OAuth2 credentials:

```env
# DVSum API Configuration
# Authentication URL for OAuth2 token exchange
DVSUM_AUTH_URL=https://auth.dvsum.ai/oauth2/token

# API Base URL for all DVSum API calls
DVSUM_API_BASE_URL=https://apis.dvsum.ai

# OAuth2 Client Credentials (required)
# Obtain these from your DVSum account settings
DVSUM_CLIENT_ID=your_client_id_here
DVSUM_CLIENT_SECRET=your_client_secret_here

# Optional: Tenant ID for multi-tenant setups
DVSUM_TENANT_ID=your_tenant_id_here

# AI Agent WebSocket URL (for real-time AI queries)
DVSUM_WEBSOCKET_URL=wss://17ew4pfncd.execute-api.us-west-2.amazonaws.com/prod

# Server Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=True
```

### Authentication

DVSum uses OAuth2 client credentials flow:
1. Your `DVSUM_CLIENT_ID` and `DVSUM_CLIENT_SECRET` are combined and base64 encoded
2. A token is obtained from the auth endpoint (`https://auth.dvsum.ai/oauth2/token`)
3. The access token is automatically refreshed when expired

Alternatively, you can configure the API credentials through the Settings page in the GUI.

## Running the Application

1. Start the server:
```bash
python run.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

## Usage

### AI Chat Interface

The main interface is a chat-based system where you can:
- Ask natural language questions about your data
- Request analysis and reports
- Trigger troubleshooting diagnostics
- Execute workflows

Example prompts:
- "Show me all available agents"
- "Analyze data quality issues"
- "Run a troubleshooting diagnostic"
- "Create a summary report"

### Managing Agents

Navigate to the Agents section to:
- View all configured AI agents
- Create new agents with custom rules
- Execute agents with specific inputs

### Workflows

The Workflows section allows you to:
- Create automated workflows
- Configure triggers (manual, scheduled, event-based)
- Execute and monitor workflow runs

### Data Sources

Connect various data sources:
- Databases
- APIs
- File systems
- Data lakes

### Data Quality

Monitor data quality:
- Run DQ checks
- View exceptions by severity
- Track quality metrics over time

## Possible Automations

Based on the DVSum API, here are the automations you can build:

### 1. Data Governance Automations
- **Auto-classify new columns**: Automatically apply data classification tags when new columns are discovered
- **Bulk update asset metadata**: Mass update descriptions, owners, stewards across multiple assets
- **Automated term linking**: Link glossary terms to columns based on naming patterns

### 2. Data Quality Automations
- **Scheduled profiling jobs**: Run data profiling on a schedule
- **Exception alerting**: Monitor and alert on DQ exceptions
- **Auto-remediation workflows**: Trigger workflows when quality thresholds are breached

### 3. Workflow Automations
- **Approval automation**: Auto-approve/reject based on rules
- **Scheduled job execution**: Run integration jobs on schedule
- **Chain workflows**: Execute dependent workflows sequentially

### 4. Dashboard & Reporting
- **Auto-generate reports**: Create widgets and dashboards programmatically
- **Scheduled exports**: Export audit logs and analytics on schedule
- **Custom analytics dashboards**: Build real-time monitoring dashboards

### 5. AI Agent Automations
- **Automated analysis**: Run AI queries on schedule
- **Chatbot integration**: Integrate with Slack/Teams for data questions
- **Smart alerts**: AI-powered anomaly detection and alerting

### 6. Asset Lifecycle Management
- **Auto-deprecation**: Mark unused assets as deprecated
- **Lineage tracking**: Automatically update relationships
- **Change tracking**: Monitor and report on asset changes via audit trail

## Project Structure

```
AgenticTool/
├── app/
│   ├── __init__.py
│   ├── main.py           # Flask application
│   ├── dvsum_client.py   # DVSum API client (OAuth2)
│   └── agentic_engine.py # Agentic AI engine
├── static/
│   ├── index.html        # Main HTML page
│   ├── css/
│   │   └── styles.css    # Application styles
│   └── js/
│       └── app.js        # Frontend JavaScript
├── .env.example          # Environment template
├── .gitignore
├── requirements.txt
├── run.py                # Entry point
└── README.md
```

## API Endpoints

The application exposes the following API endpoints:

### Configuration
- `GET /api/config` - Get configuration status
- `POST /api/config` - Set API configuration (client_id, client_secret)
- `POST /api/test-connection` - Test API connection

### Agentic AI
- `POST /api/agentic/process` - Process natural language requests
- `GET /api/agentic/history` - Get execution history
- `POST /api/agentic/clear` - Clear history

### Agents
- `GET /api/agents` - List all agents
- `POST /api/agents` - Create new agent
- `GET /api/agents/<id>` - Get agent details
- `POST /api/agents/<id>/execute` - Execute agent
- `POST /api/agents/<id>/chat` - Chat with agent

### Workflows
- `GET /api/workflows` - List all workflows
- `POST /api/workflows` - Create new workflow
- `POST /api/workflows/<id>/execute` - Execute workflow

### Data Sources
- `GET /api/datasources` - List data sources
- `POST /api/datasources` - Connect data source

### Data Quality
- `POST /api/dataquality/check` - Run DQ check
- `GET /api/dataquality/exceptions` - Get DQ exceptions

## DVSum API Reference

The DVSumClient supports the following API categories:

| Category | Description |
|----------|-------------|
| Dashboard | Manage dashboards and widgets |
| Asset Listing | Governance views, search, mass updates |
| Assets (Nodes) | CRUD for Terms, Tables, Columns, Rules |
| Workflow | Approval workflows (submit, approve, reject) |
| AI Agent | Execute AI queries via WebSocket |
| Job Execution | Run and monitor integration jobs |
| Audit Trail | Query and export audit logs |

### Node Types
| Code | Type |
|------|------|
| TRM | Glossary Term |
| TBL | Table |
| COL | Column |
| RLS | Rules |
| DSR | Dataset/Report |
| ANL | Analysis/ChatBots |
| RFD | Reference Dictionary |
| JOB | Jobs |
| SCH | Executions |

## Development

To run in development mode with auto-reload:
```bash
FLASK_DEBUG=True python run.py
```

## License

MIT License

## Support

- DVSum API Documentation: https://apis-doc.dvsum.ai/
- For issues with this tool, please open a GitHub issue
