"""
DVSum API Client
Handles all communication with the DVSum API for agentic AI automation.
Uses OAuth2 client credentials flow for authentication.
"""

import requests
import base64
import time
from typing import Optional, Dict, Any, List


class DVSumClient:
    """Client for interacting with DVSum's Agentic AI APIs."""

    # Default URLs
    DEFAULT_AUTH_URL = "https://auth.dvsum.ai/oauth2/token"
    DEFAULT_API_URL = "https://apis.dvsum.ai"
    DEFAULT_WEBSOCKET_URL = "wss://17ew4pfncd.execute-api.us-west-2.amazonaws.com/prod"

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        base_url: Optional[str] = None,
        auth_url: Optional[str] = None,
        tenant_id: Optional[str] = None,
        websocket_url: Optional[str] = None
    ):
        """
        Initialize the DVSum API client with OAuth2 credentials.

        Args:
            client_id: DVSum OAuth2 client ID
            client_secret: DVSum OAuth2 client secret
            base_url: The DVSum API base URL (default: https://apis.dvsum.ai)
            auth_url: The DVSum Auth URL (default: https://auth.dvsum.ai/oauth2/token)
            tenant_id: Optional tenant ID for multi-tenant setups
            websocket_url: WebSocket URL for AI Agent (default: wss://...)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = (base_url or self.DEFAULT_API_URL).rstrip('/')
        self.auth_url = auth_url or self.DEFAULT_AUTH_URL
        self.tenant_id = tenant_id
        self.websocket_url = websocket_url or self.DEFAULT_WEBSOCKET_URL

        # Token management
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0

        # Session for API requests
        self.session = requests.Session()
        self._setup_base_headers()

    def _setup_base_headers(self):
        """Setup base headers for API requests."""
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        })
        if self.tenant_id:
            self.session.headers['X-Tenant-ID'] = self.tenant_id

    def _get_basic_auth_header(self) -> str:
        """
        Generate Basic Auth header for OAuth2 token request.
        Combines client_id:client_secret and base64 encodes it.
        """
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        return f"Basic {encoded}"

    def _refresh_token(self) -> bool:
        """
        Refresh the OAuth2 access token using client credentials flow.

        Returns:
            True if token was successfully refreshed, False otherwise.
        """
        try:
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': self._get_basic_auth_header()
            }

            data = {
                'grant_type': 'client_credentials'
            }

            response = requests.post(
                self.auth_url,
                headers=headers,
                data=data,
                timeout=30
            )
            response.raise_for_status()

            token_data = response.json()
            self._access_token = token_data.get('access_token')

            # Calculate token expiry (with 60 second buffer)
            expires_in = token_data.get('expires_in', 3600)
            self._token_expires_at = time.time() + expires_in - 60

            # Update session authorization header
            self.session.headers['Authorization'] = f"Bearer {self._access_token}"

            return True

        except requests.exceptions.RequestException as e:
            print(f"Failed to refresh token: {e}")
            return False

    def _ensure_valid_token(self) -> bool:
        """
        Ensure we have a valid access token.
        Refreshes the token if expired or not present.

        Returns:
            True if we have a valid token, False otherwise.
        """
        if self._access_token and time.time() < self._token_expires_at:
            return True
        return self._refresh_token()

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        require_auth: bool = True
    ) -> Dict[str, Any]:
        """
        Make an API request to DVSum.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters
            require_auth: Whether to require authentication (default: True)

        Returns:
            API response as dictionary
        """
        # Ensure we have a valid token
        if require_auth and not self._ensure_valid_token():
            return {
                'success': False,
                'error': 'Failed to authenticate with DVSum API',
                'status_code': 401
            }

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

    # ==================== Connection Testing ====================

    def test_connection(self) -> Dict[str, Any]:
        """Test the API connection with current credentials."""
        if self._ensure_valid_token():
            return {
                'success': True,
                'message': 'Successfully authenticated with DVSum API',
                'token_expires_at': self._token_expires_at
            }
        return {
            'success': False,
            'error': 'Failed to authenticate with DVSum API'
        }

    def health_check(self) -> Dict[str, Any]:
        """Check API health status."""
        result = self.test_connection()
        if result['success']:
            result['api_url'] = self.base_url
            result['auth_url'] = self.auth_url
        return result

    # ==================== Dashboard Management ====================

    def list_dashboards(self) -> Dict[str, Any]:
        """List all available dashboards."""
        return self._make_request('GET', '/dashboard')

    def get_current_dashboard(self) -> Dict[str, Any]:
        """Get the current dashboard view."""
        return self._make_request('GET', '/dashboard/current')

    def set_current_dashboard(self, dashboard_id: int) -> Dict[str, Any]:
        """Set a dashboard as the current view."""
        return self._make_request('POST', f'/dashboard/{dashboard_id}/current')

    def get_dashboard_widgets(self, dashboard_id: int) -> Dict[str, Any]:
        """Get all widgets for a dashboard."""
        return self._make_request('GET', f'/dashboard/{dashboard_id}/widgets')

    def create_widget(self, dashboard_id: int, widget_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new widget on a dashboard."""
        return self._make_request('POST', f'/dashboard/{dashboard_id}/widgets', data=widget_config)

    def get_widget_data(
        self,
        dashboard_id: int,
        widget_id: int,
        time_zone: int = -300,
        size: Optional[int] = None,
        offset: Optional[int] = None,
        sort_key: Optional[str] = None,
        sort_by: str = 'asc'
    ) -> Dict[str, Any]:
        """Get data for a specific widget."""
        params = {'time_zone': time_zone, 'sortBy': sort_by}
        if size:
            params['size'] = size
        if offset:
            params['offset'] = offset
        if sort_key:
            params['sortKey'] = sort_key
        return self._make_request('GET', f'/dashboard/{dashboard_id}/widgets/{widget_id}/data', params=params)

    def delete_widget(self, dashboard_id: int, widget_id: int) -> Dict[str, Any]:
        """Delete a widget from a dashboard."""
        return self._make_request('DELETE', f'/dashboard/{dashboard_id}/widgets/{widget_id}')

    # ==================== Asset Listing ====================

    def get_governance_views(self, node_type: str, node_id: Optional[int] = None) -> Dict[str, Any]:
        """Get governance views for a specific asset type."""
        params = {'node_type': node_type}
        if node_id:
            params['node_id'] = node_id
        return self._make_request('GET', '/node-listing/gov-view', params=params)

    def get_current_governance_view(self, node_type: str, node_id: Optional[int] = None) -> Dict[str, Any]:
        """Get the current governance view configuration."""
        params = {'node_type': node_type}
        if node_id:
            params['node_id'] = node_id
        return self._make_request('GET', '/node-listing/gov-view/get-current', params=params)

    def search_asset_listing(
        self,
        search_id: int,
        page_number: int = 1,
        page_size: int = 50,
        sort_model: Optional[List[Dict]] = None,
        filter_model: Optional[Dict] = None,
        count_filter: str = 'all',
        mandatory_fields: Optional[List[str]] = None,
        timezone: int = -300
    ) -> Dict[str, Any]:
        """Search asset listing data."""
        payload = {
            'pageNumber': page_number,
            'pageSize': page_size,
            'sortModel': sort_model or [],
            'filterModel': filter_model or {},
            'countFilter': count_filter,
            'mandatory_fields': mandatory_fields or [],
            'timezone': timezone
        }
        return self._make_request('POST', f'/node-listing/listing/{search_id}/data', data=payload)

    def get_filter_values(
        self,
        search_id: int,
        field_id: int,
        node_type: str,
        filter_model: Optional[Dict] = None,
        count_filter: str = 'all',
        node_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get filter dropdown values for asset listing."""
        params = {
            'field_id': field_id,
            'node_type': node_type
        }
        if node_id:
            params['node_id'] = node_id
        payload = {
            'filterModel': filter_model or {},
            'countFilter': count_filter
        }
        return self._make_request('POST', f'/node-listing/listing/{search_id}/filter-values', data=payload, params=params)

    def mass_update_fields(
        self,
        node_type: str,
        search_id: int,
        update_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Perform mass update on assets."""
        params = {
            'node_type': node_type,
            'search_id': search_id
        }
        return self._make_request('PUT', '/node-listing/listing/fields-data-update', data=update_data, params=params)

    def get_mass_update_fields(
        self,
        node_type: str,
        tags: bool = False,
        dcl: bool = False
    ) -> Dict[str, Any]:
        """Get fields available for mass update."""
        params = {'node_type': node_type}
        if tags:
            params['tags'] = 'true'
        if dcl:
            params['dcl'] = 'true'
        return self._make_request('GET', '/node-listing/listing/fields-values', params=params)

    # ==================== Assets (Nodes) ====================

    def search_assets(
        self,
        node_type: str,
        search_text: str,
        node_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Search for assets by type and context."""
        params = {
            'node-type': node_type,
            'search-text': search_text
        }
        if node_context:
            params['node-context'] = node_context
        return self._make_request('GET', '/nodes/search', params=params)

    def create_asset(self, node_type: str, asset_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new asset."""
        params = {'node-type': node_type}
        return self._make_request('POST', '/nodes', data=asset_data, params=params)

    def get_asset_details(
        self,
        node_id: int,
        node_type: str,
        node_status: str = 'PUB'
    ) -> Dict[str, Any]:
        """Get details of a specific asset."""
        params = {
            'node-id': node_id,
            'node-type': node_type,
            'node-status': node_status
        }
        return self._make_request('GET', '/nodes/details', params=params)

    def update_asset_details(
        self,
        node_id: int,
        node_type: str,
        asset_data: Dict[str, Any],
        node_status: str = 'PUB'
    ) -> Dict[str, Any]:
        """Update asset details."""
        params = {
            'node-id': node_id,
            'node-type': node_type,
            'node-status': node_status
        }
        return self._make_request('PUT', '/nodes/details', data=asset_data, params=params)

    def review_asset_changes(self, node_id: int, node_type: Optional[str] = None) -> Dict[str, Any]:
        """Review changes between published and draft versions."""
        params = {}
        if node_type:
            params['node_type'] = node_type
        return self._make_request('GET', f'/nodes/{node_id}/review', params=params)

    def get_asset_relationships(self, node_id: int, status: str = 'PUB') -> Dict[str, Any]:
        """Get lineage relationships for a node."""
        params = {'status': status}
        return self._make_request('GET', f'/nodes/{node_id}/relationships', params=params)

    def get_similar_assets(self, node_id: int) -> Dict[str, Any]:
        """Get assets similar to a given node."""
        return self._make_request('GET', f'/nodes/{node_id}/similar-assets')

    # ==================== Workflow ====================

    def get_workflow_steps(
        self,
        workflow_id: str,
        node_type: str,
        node_id: int
    ) -> Dict[str, Any]:
        """Get workflow steps and current status."""
        params = {
            'node_type': node_type,
            'node_id': node_id
        }
        return self._make_request('GET', f'/workflow/{workflow_id}/steps', params=params)

    def perform_workflow_action(
        self,
        workflow_id: int,
        action: str,
        node_id: int,
        node_type: str,
        comment: str = ""
    ) -> Dict[str, Any]:
        """
        Perform workflow action (approve, reject, submit, cancel).

        Args:
            workflow_id: Workflow instance ID
            action: Action to perform (APR, REJ, SMT, CSB)
            node_id: Node ID
            node_type: Node type
            comment: Required comment for the action
        """
        params = {
            'in_action': action,
            'node_id': node_id,
            'node_type': node_type
        }
        payload = {'comment': comment}
        return self._make_request('PUT', f'/workflow/{workflow_id}/action', data=payload, params=params)

    # ==================== AI Agent / Data Analysis ====================

    def execute_ai_query(
        self,
        query_id: int,
        analysis_id: int,
        connection_id: str,
        messages: List[Dict[str, str]],
        audience_type: str = 'DEFAULT',
        response_type: str = 'JSON',
        properties: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Execute an AI Agent query.

        Note: This initiates the query. Results are returned via WebSocket.
        """
        payload = {
            'analysis_id': analysis_id,
            'connection_id': connection_id,
            'audience_type': audience_type,
            'response_type': response_type,
            'messages': messages,
            'properties': properties or {}
        }
        return self._make_request('POST', f'/data-analysis/queries/{query_id}/execute', data=payload)

    def get_questions_history(
        self,
        number_of_days: int = 7,
        analysis_id: Optional[int] = None,
        export_as_file: bool = False
    ) -> Dict[str, Any]:
        """Get AI agent questions history."""
        params = {
            'number-of-days': number_of_days,
            'export-as-file': str(export_as_file).lower()
        }
        if analysis_id:
            params['analysis-id'] = analysis_id
        return self._make_request('GET', '/data-analysis/questions-history', params=params)

    # ==================== Job Execution ====================

    def execute_job(self, job_id: int) -> Dict[str, Any]:
        """Execute an integration job."""
        return self._make_request('POST', f'/integration/jobs/{job_id}/execute')

    def get_job_execution_details(self, execution_id: int) -> Dict[str, Any]:
        """Get job execution details."""
        return self._make_request('GET', f'/integration/jobs/{execution_id}/details')

    def delete_jobs(
        self,
        node_ids: List[int],
        is_mass_update: bool = False,
        is_select_all: bool = False
    ) -> Dict[str, Any]:
        """Delete one or more jobs."""
        params = {'node_type': 'JOB'}
        payload = [{
            'node_ids': node_ids,
            'is_mass_update': is_mass_update,
            'isSelectAll': is_select_all,
            'countFilter': 'all',
            'field': 'job_status',
            'job_status': 'DEL'
        }]
        return self._make_request('PUT', '/node-listing/listing/fields-data-update', data=payload, params=params)

    # ==================== Audit Trail ====================

    def get_audit_logs(
        self,
        entity_type: str,
        entity_id: str,
        page_size: int = 100,
        next_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get audit logs for a specific entity."""
        params = {
            'entity_type': entity_type,
            'entity_id': entity_id,
            'page_size': page_size
        }
        if next_token:
            params['next_token'] = next_token
        return self._make_request('GET', '/audit-trail/audit-logs', params=params)

    def query_audit_logs(
        self,
        account_id: str,
        user_id: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        event_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        page_size: int = 50,
        forward_direction: bool = False,
        next_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Query audit logs with filtering."""
        payload = {
            'account_id': account_id,
            'page_size': page_size,
            'forward_direction': forward_direction
        }
        if user_id:
            payload['user_id'] = user_id
        if entity_type:
            payload['entity_type'] = entity_type
        if entity_id:
            payload['entity_id'] = entity_id
        if event_type:
            payload['event_type'] = event_type
        if start_date:
            payload['start_date'] = start_date
        if end_date:
            payload['end_date'] = end_date
        if next_token:
            payload['next_token'] = next_token
        return self._make_request('POST', '/audit-trail/audit-logs', data=payload)

    def export_audit_logs_csv(
        self,
        account_id: str,
        connection_id: str,
        file_name: str = 'audit_logs',
        max_record_count: int = 100000,
        **filters
    ) -> Dict[str, Any]:
        """Export audit logs to CSV."""
        payload = {
            'account_id': account_id,
            'connection_id': connection_id,
            'file_name': file_name,
            'max_record_count': max_record_count,
            **filters
        }
        return self._make_request('POST', '/audit-trail/audit-logs/export-csv', data=payload)

    # ==================== Legacy Methods (for backward compatibility) ====================

    def list_agents(self) -> Dict[str, Any]:
        """List all available AI agents (analyses)."""
        # This would map to data-analysis endpoints
        return self._make_request('GET', '/data-analysis/agents')

    def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """Get details of a specific agent."""
        return self._make_request('GET', f'/data-analysis/agents/{agent_id}')

    def create_agent(self, agent_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new AI agent."""
        return self._make_request('POST', '/data-analysis/agents', data=agent_config)

    def list_data_sources(self) -> Dict[str, Any]:
        """List all connected data sources."""
        return self.get_governance_views('SRC')

    def connect_data_source(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Connect a new data source."""
        return self.create_asset('SRC', config)

    def query_data(self, query: str, data_source_id: Optional[str] = None) -> Dict[str, Any]:
        """Execute a natural language query."""
        # This would need to use the AI Agent WebSocket flow
        return {
            'success': False,
            'error': 'Use execute_ai_query with WebSocket for natural language queries'
        }

    def list_workflows(self) -> Dict[str, Any]:
        """List all workflows."""
        return self.get_governance_views('JOB')

    def create_workflow(self, workflow_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new workflow."""
        return self.create_asset('JOB', workflow_config)

    def execute_workflow(
        self,
        workflow_id: str,
        input_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a workflow."""
        return self.execute_job(int(workflow_id))

    def run_data_quality_check(
        self,
        data_source_id: str,
        rules: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Run data quality checks (profiling)."""
        # Map to the profiling job execution
        return {
            'success': False,
            'error': 'Use execute_job for profiling jobs'
        }

    def get_dq_exceptions(self, data_source_id: Optional[str] = None) -> Dict[str, Any]:
        """Get data quality exceptions."""
        return self.get_governance_views('RLS')

    def get_analytics(
        self,
        metric_type: str,
        date_range: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Get analytics and insights."""
        return self.list_dashboards()
