"""
DVSum Agentic AI Automation - Flask Application
Main entry point for the web application.
"""

import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

from dvsum_client import DVSumClient
from agentic_engine import AgenticEngine

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_folder='../static', static_url_path='')
CORS(app)

# Global instances (initialized on first use or configuration)
dvsum_client = None
agentic_engine = None


def _parse_ssl_verify(value) -> bool | str | None:
    """Parse SSL verify value from config or environment."""
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        if value.lower() in ('true', '1', 'yes', 'on'):
            return True
        elif value.lower() in ('false', '0', 'no', 'off'):
            return False
        elif os.path.exists(value):
            # Treat as path to CA bundle
            return value
    return None


def get_dvsum_client(config: dict = None) -> DVSumClient:
    """Get or create DVSum client instance."""
    global dvsum_client

    if config:
        # Parse SSL verify setting from config
        ssl_verify = _parse_ssl_verify(config.get('ssl_verify'))

        # Configuration provided via API
        dvsum_client = DVSumClient(
            client_id=config.get('client_id', os.getenv('DVSUM_CLIENT_ID', '')),
            client_secret=config.get('client_secret', os.getenv('DVSUM_CLIENT_SECRET', '')),
            base_url=config.get('base_url', os.getenv('DVSUM_API_BASE_URL')),
            auth_url=config.get('auth_url', os.getenv('DVSUM_AUTH_URL')),
            tenant_id=config.get('tenant_id', os.getenv('DVSUM_TENANT_ID')),
            websocket_url=config.get('websocket_url', os.getenv('DVSUM_WEBSOCKET_URL')),
            ssl_verify=ssl_verify
        )
    elif dvsum_client is None:
        # Initialize from environment variables
        client_id = os.getenv('DVSUM_CLIENT_ID', '')
        client_secret = os.getenv('DVSUM_CLIENT_SECRET', '')
        if client_id and client_secret:
            dvsum_client = DVSumClient(
                client_id=client_id,
                client_secret=client_secret,
                base_url=os.getenv('DVSUM_API_BASE_URL'),
                auth_url=os.getenv('DVSUM_AUTH_URL'),
                tenant_id=os.getenv('DVSUM_TENANT_ID'),
                websocket_url=os.getenv('DVSUM_WEBSOCKET_URL'),
                ssl_verify=None  # Will auto-detect from env vars
            )

    return dvsum_client


def get_agentic_engine() -> AgenticEngine:
    """Get or create Agentic Engine instance."""
    global agentic_engine

    client = get_dvsum_client()
    if client and (agentic_engine is None or agentic_engine.client != client):
        agentic_engine = AgenticEngine(client)

    return agentic_engine


# ==================== Static Routes ====================

@app.route('/')
def index():
    """Serve the main application page."""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/<path:path>')
def static_files(path):
    """Serve static files."""
    return send_from_directory(app.static_folder, path)


# ==================== Configuration Routes ====================

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration status."""
    client = get_dvsum_client()
    return jsonify({
        'configured': client is not None,
        'base_url': client.base_url if client else os.getenv('DVSUM_API_BASE_URL', ''),
        'auth_url': client.auth_url if client else os.getenv('DVSUM_AUTH_URL', ''),
        'websocket_url': client.websocket_url if client else os.getenv('DVSUM_WEBSOCKET_URL', '')
    })


@app.route('/api/config', methods=['POST'])
def set_config():
    """Set DVSum API configuration."""
    data = request.json

    if not data.get('client_id') or not data.get('client_secret'):
        return jsonify({
            'success': False,
            'error': 'client_id and client_secret are required'
        }), 400

    try:
        client = get_dvsum_client(data)
        # Test the connection
        test_result = client.test_connection()
        if test_result.get('success'):
            return jsonify({
                'success': True,
                'message': 'Configuration saved and authenticated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': test_result.get('error', 'Authentication failed')
            }), 401
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/test-connection', methods=['POST'])
def test_connection():
    """Test the DVSum API connection."""
    client = get_dvsum_client()

    if not client:
        return jsonify({
            'success': False,
            'error': 'DVSum client not configured'
        }), 400

    result = client.test_connection()
    return jsonify(result)


# ==================== Agent Routes ====================

@app.route('/api/agents', methods=['GET'])
def list_agents():
    """List all available agents."""
    client = get_dvsum_client()
    if not client:
        return jsonify({'success': False, 'error': 'Not configured'}), 400

    result = client.list_agents()
    return jsonify(result)


@app.route('/api/agents/<agent_id>', methods=['GET'])
def get_agent(agent_id):
    """Get a specific agent."""
    client = get_dvsum_client()
    if not client:
        return jsonify({'success': False, 'error': 'Not configured'}), 400

    result = client.get_agent(agent_id)
    return jsonify(result)


@app.route('/api/agents', methods=['POST'])
def create_agent():
    """Create a new agent."""
    client = get_dvsum_client()
    if not client:
        return jsonify({'success': False, 'error': 'Not configured'}), 400

    result = client.create_agent(request.json)
    return jsonify(result)


@app.route('/api/agents/<agent_id>/execute', methods=['POST'])
def execute_agent(agent_id):
    """Execute an agent."""
    client = get_dvsum_client()
    if not client:
        return jsonify({'success': False, 'error': 'Not configured'}), 400

    data = request.json or {}
    result = client.execute_agent(
        agent_id,
        data.get('input', {}),
        data.get('context')
    )
    return jsonify(result)


@app.route('/api/agents/<agent_id>/chat', methods=['POST'])
def chat_with_agent(agent_id):
    """Chat with an agent."""
    client = get_dvsum_client()
    if not client:
        return jsonify({'success': False, 'error': 'Not configured'}), 400

    data = request.json
    result = client.chat_with_agent(
        agent_id,
        data.get('message', ''),
        data.get('conversation_id')
    )
    return jsonify(result)


# ==================== Agentic AI Routes ====================

@app.route('/api/agentic/process', methods=['POST'])
def agentic_process():
    """Process a message through the agentic AI engine."""
    engine = get_agentic_engine()
    if not engine:
        return jsonify({
            'success': False,
            'error': 'Agentic engine not available. Please configure DVSum API first.'
        }), 400

    data = request.json
    message = data.get('message', '')

    if not message:
        return jsonify({
            'success': False,
            'error': 'Message is required'
        }), 400

    result = engine.process_message(message)
    return jsonify(result)


@app.route('/api/agentic/history', methods=['GET'])
def agentic_history():
    """Get agentic execution history."""
    engine = get_agentic_engine()
    if not engine:
        return jsonify({'history': []})

    return jsonify({'history': engine.get_execution_history()})


@app.route('/api/agentic/clear', methods=['POST'])
def agentic_clear():
    """Clear agentic history."""
    engine = get_agentic_engine()
    if engine:
        engine.clear_history()

    return jsonify({'success': True, 'message': 'History cleared'})


# ==================== Data Routes ====================

@app.route('/api/datasources', methods=['GET'])
def list_data_sources():
    """List all data sources."""
    client = get_dvsum_client()
    if not client:
        return jsonify({'success': False, 'error': 'Not configured'}), 400

    result = client.list_data_sources()
    return jsonify(result)


@app.route('/api/datasources', methods=['POST'])
def connect_data_source():
    """Connect a new data source."""
    client = get_dvsum_client()
    if not client:
        return jsonify({'success': False, 'error': 'Not configured'}), 400

    result = client.connect_data_source(request.json)
    return jsonify(result)


@app.route('/api/query', methods=['POST'])
def query_data():
    """Execute a natural language query."""
    client = get_dvsum_client()
    if not client:
        return jsonify({'success': False, 'error': 'Not configured'}), 400

    data = request.json
    result = client.query_data(
        data.get('query', ''),
        data.get('data_source_id')
    )
    return jsonify(result)


# ==================== Workflow Routes ====================

@app.route('/api/workflows', methods=['GET'])
def list_workflows():
    """List all workflows."""
    client = get_dvsum_client()
    if not client:
        return jsonify({'success': False, 'error': 'Not configured'}), 400

    result = client.list_workflows()
    return jsonify(result)


@app.route('/api/workflows', methods=['POST'])
def create_workflow():
    """Create a new workflow."""
    client = get_dvsum_client()
    if not client:
        return jsonify({'success': False, 'error': 'Not configured'}), 400

    result = client.create_workflow(request.json)
    return jsonify(result)


@app.route('/api/workflows/<workflow_id>/execute', methods=['POST'])
def execute_workflow(workflow_id):
    """Execute a workflow."""
    client = get_dvsum_client()
    if not client:
        return jsonify({'success': False, 'error': 'Not configured'}), 400

    result = client.execute_workflow(workflow_id, request.json)
    return jsonify(result)


# ==================== Dashboard Routes ====================

@app.route('/api/dashboards', methods=['GET'])
def list_dashboards():
    """List all available dashboards."""
    client = get_dvsum_client()
    if not client:
        return jsonify({'success': False, 'error': 'Not configured'}), 400

    result = client.list_dashboards()
    return jsonify(result)


@app.route('/api/dashboards/current', methods=['GET'])
def get_current_dashboard():
    """Get the current dashboard."""
    client = get_dvsum_client()
    if not client:
        return jsonify({'success': False, 'error': 'Not configured'}), 400

    result = client.get_current_dashboard()
    return jsonify(result)


@app.route('/api/dashboards/<int:dashboard_id>/current', methods=['POST'])
def set_current_dashboard(dashboard_id):
    """Set a dashboard as the current view."""
    client = get_dvsum_client()
    if not client:
        return jsonify({'success': False, 'error': 'Not configured'}), 400

    result = client.set_current_dashboard(dashboard_id)
    return jsonify(result)


@app.route('/api/dashboards/<int:dashboard_id>/widgets', methods=['GET'])
def get_dashboard_widgets(dashboard_id):
    """Get all widgets for a dashboard."""
    client = get_dvsum_client()
    if not client:
        return jsonify({'success': False, 'error': 'Not configured'}), 400

    result = client.get_dashboard_widgets(dashboard_id)
    return jsonify(result)


@app.route('/api/dashboards/<int:dashboard_id>/widgets', methods=['POST'])
def create_widget(dashboard_id):
    """Create a new widget on a dashboard."""
    client = get_dvsum_client()
    if not client:
        return jsonify({'success': False, 'error': 'Not configured'}), 400

    result = client.create_widget(dashboard_id, request.json)
    return jsonify(result)


@app.route('/api/dashboards/<int:dashboard_id>/widgets/<int:widget_id>/data', methods=['GET'])
def get_widget_data(dashboard_id, widget_id):
    """Get data for a specific widget."""
    client = get_dvsum_client()
    if not client:
        return jsonify({'success': False, 'error': 'Not configured'}), 400

    time_zone = request.args.get('time_zone', -300, type=int)
    size = request.args.get('size', type=int)
    offset = request.args.get('offset', type=int)
    sort_key = request.args.get('sort_key')
    sort_by = request.args.get('sort_by', 'asc')

    result = client.get_widget_data(
        dashboard_id,
        widget_id,
        time_zone=time_zone,
        size=size,
        offset=offset,
        sort_key=sort_key,
        sort_by=sort_by
    )
    return jsonify(result)


@app.route('/api/dashboards/<int:dashboard_id>/widgets/<int:widget_id>', methods=['DELETE'])
def delete_widget(dashboard_id, widget_id):
    """Delete a widget from a dashboard."""
    client = get_dvsum_client()
    if not client:
        return jsonify({'success': False, 'error': 'Not configured'}), 400

    result = client.delete_widget(dashboard_id, widget_id)
    return jsonify(result)


# ==================== Data Quality Routes ====================

@app.route('/api/dataquality/check', methods=['POST'])
def run_dq_check():
    """Run a data quality check."""
    client = get_dvsum_client()
    if not client:
        return jsonify({'success': False, 'error': 'Not configured'}), 400

    data = request.json
    result = client.run_data_quality_check(
        data.get('data_source_id', ''),
        data.get('rules')
    )
    return jsonify(result)


@app.route('/api/dataquality/exceptions', methods=['GET'])
def get_dq_exceptions():
    """Get data quality exceptions."""
    client = get_dvsum_client()
    if not client:
        return jsonify({'success': False, 'error': 'Not configured'}), 400

    result = client.get_dq_exceptions(request.args.get('data_source_id'))
    return jsonify(result)


# ==================== Analytics Routes ====================

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get analytics data."""
    client = get_dvsum_client()
    if not client:
        return jsonify({'success': False, 'error': 'Not configured'}), 400

    metric_type = request.args.get('metric_type', 'usage')
    date_range = {}
    if request.args.get('start_date'):
        date_range['start_date'] = request.args.get('start_date')
    if request.args.get('end_date'):
        date_range['end_date'] = request.args.get('end_date')

    result = client.get_analytics(metric_type, date_range if date_range else None)
    return jsonify(result)


# ==================== Health Routes ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Check application health."""
    client = get_dvsum_client()

    status = {
        'status': 'healthy',
        'dvsum_configured': client is not None
    }

    if client:
        dvsum_health = client.health_check()
        status['dvsum_health'] = dvsum_health

    return jsonify(status)


# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5001))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

    print(f"Starting DVSum Agentic AI Automation Tool on {host}:{port}")
    app.run(host=host, port=port, debug=debug)
