"""
DVSum API Client
Handles all communication with the DVSum API for agentic AI automation.
"""

import requests
from typing import Optional, Dict, Any, List
import json


class DVSumClient:
    """Client for interacting with DVSum's Agentic AI APIs."""

    def __init__(self, base_url: str, api_key: str, tenant_id: Optional[str] = None):
        """
        Initialize the DVSum API client.

        Args:
            base_url: The DVSum API base URL
            api_key: Your DVSum API key
            tenant_id: Optional tenant ID for multi-tenant setups
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.tenant_id = tenant_id
        self.session = requests.Session()
        self._setup_headers()

    def _setup_headers(self):
        """Setup default headers for API requests."""
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        })
        if self.tenant_id:
            self.session.headers['X-Tenant-ID'] = self.tenant_id

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make an API request to DVSum.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters

        Returns:
            API response as dictionary
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return {
                'success': True,
                'data': response.json() if response.text else {},
                'status_code': response.status_code
            }
        except requests.exceptions.HTTPError as e:
            return {
                'success': False,
                'error': str(e),
                'status_code': e.response.status_code if e.response else None,
                'details': e.response.text if e.response else None
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'status_code': None
            }

    # ==================== Agent Management ====================

    def list_agents(self) -> Dict[str, Any]:
        """List all available AI agents."""
        return self._make_request('GET', '/api/v1/agents')

    def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """Get details of a specific agent."""
        return self._make_request('GET', f'/api/v1/agents/{agent_id}')

    def create_agent(self, agent_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new AI agent.

        Args:
            agent_config: Agent configuration including name, type, rules, etc.
        """
        return self._make_request('POST', '/api/v1/agents', data=agent_config)

    def update_agent(self, agent_id: str, agent_config: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing agent."""
        return self._make_request('PUT', f'/api/v1/agents/{agent_id}', data=agent_config)

    def delete_agent(self, agent_id: str) -> Dict[str, Any]:
        """Delete an agent."""
        return self._make_request('DELETE', f'/api/v1/agents/{agent_id}')

    # ==================== Agent Execution ====================

    def execute_agent(
        self,
        agent_id: str,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute an AI agent with given input.

        Args:
            agent_id: ID of the agent to execute
            input_data: Input data for the agent
            context: Optional execution context
        """
        payload = {
            'input': input_data,
            'context': context or {}
        }
        return self._make_request('POST', f'/api/v1/agents/{agent_id}/execute', data=payload)

    def chat_with_agent(
        self,
        agent_id: str,
        message: str,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a chat message to an agent.

        Args:
            agent_id: ID of the agent
            message: User message
            conversation_id: Optional conversation ID for context continuity
        """
        payload = {
            'message': message,
            'conversation_id': conversation_id
        }
        return self._make_request('POST', f'/api/v1/agents/{agent_id}/chat', data=payload)

    # ==================== Data Connections ====================

    def list_data_sources(self) -> Dict[str, Any]:
        """List all connected data sources."""
        return self._make_request('GET', '/api/v1/datasources')

    def connect_data_source(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Connect a new data source.

        Args:
            config: Data source configuration
        """
        return self._make_request('POST', '/api/v1/datasources', data=config)

    def query_data(self, query: str, data_source_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a natural language query against data sources.

        Args:
            query: Natural language query
            data_source_id: Optional specific data source to query
        """
        payload = {
            'query': query,
            'data_source_id': data_source_id
        }
        return self._make_request('POST', '/api/v1/query', data=payload)

    # ==================== Workflows & Automations ====================

    def list_workflows(self) -> Dict[str, Any]:
        """List all automation workflows."""
        return self._make_request('GET', '/api/v1/workflows')

    def create_workflow(self, workflow_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new automation workflow.

        Args:
            workflow_config: Workflow configuration
        """
        return self._make_request('POST', '/api/v1/workflows', data=workflow_config)

    def execute_workflow(
        self,
        workflow_id: str,
        input_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a workflow.

        Args:
            workflow_id: ID of the workflow
            input_data: Optional input parameters
        """
        return self._make_request(
            'POST',
            f'/api/v1/workflows/{workflow_id}/execute',
            data=input_data or {}
        )

    def get_workflow_status(self, execution_id: str) -> Dict[str, Any]:
        """Get the status of a workflow execution."""
        return self._make_request('GET', f'/api/v1/workflows/executions/{execution_id}')

    # ==================== Data Quality ====================

    def run_data_quality_check(
        self,
        data_source_id: str,
        rules: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Run data quality checks.

        Args:
            data_source_id: Data source to check
            rules: Optional custom DQ rules
        """
        payload = {
            'data_source_id': data_source_id,
            'rules': rules or []
        }
        return self._make_request('POST', '/api/v1/dataquality/check', data=payload)

    def get_dq_exceptions(self, data_source_id: Optional[str] = None) -> Dict[str, Any]:
        """Get data quality exceptions."""
        params = {'data_source_id': data_source_id} if data_source_id else None
        return self._make_request('GET', '/api/v1/dataquality/exceptions', params=params)

    # ==================== Analytics & Insights ====================

    def get_analytics(
        self,
        metric_type: str,
        date_range: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Get analytics and insights.

        Args:
            metric_type: Type of metric (e.g., 'usage', 'performance', 'errors')
            date_range: Optional date range filter
        """
        params = {'metric_type': metric_type}
        if date_range:
            params.update(date_range)
        return self._make_request('GET', '/api/v1/analytics', params=params)

    # ==================== Health & Status ====================

    def health_check(self) -> Dict[str, Any]:
        """Check API health status."""
        return self._make_request('GET', '/api/v1/health')

    def test_connection(self) -> Dict[str, Any]:
        """Test the API connection with current credentials."""
        return self._make_request('GET', '/api/v1/auth/test')
