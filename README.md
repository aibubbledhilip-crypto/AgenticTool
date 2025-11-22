# DVSum Agentic AI Automation Tool

A web-based GUI application for automating tasks using DVSum's Agentic AI platform. This tool provides an intuitive interface for interacting with DVSum APIs, managing AI agents, workflows, data sources, and data quality checks.

## Features

- **Agentic AI Chat**: Natural language interface to interact with DVSum's AI capabilities
- **Agent Management**: Create, view, and execute AI agents
- **Workflow Automation**: Design and run automated workflows
- **Data Source Integration**: Connect and query multiple data sources
- **Data Quality Monitoring**: Run DQ checks and view exceptions
- **Execution History**: Track all operations and their outcomes

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- DVSum API credentials

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

Edit the `.env` file with your DVSum API credentials:

```env
# DVSum API Configuration
DVSUM_API_BASE_URL=https://apis-doc.dvsum.ai
DVSUM_API_KEY=your_dvsum_api_key_here
DVSUM_TENANT_ID=your_tenant_id_here  # Optional

# Server Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=True
```

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

## Project Structure

```
AgenticTool/
├── app/
│   ├── __init__.py
│   ├── main.py           # Flask application
│   ├── dvsum_client.py   # DVSum API client
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
- `POST /api/config` - Set API configuration
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

## Development

To run in development mode with auto-reload:
```bash
FLASK_DEBUG=True python run.py
```

## License

MIT License

## Support

For DVSum API documentation, visit: https://apis-doc.dvsum.ai/
