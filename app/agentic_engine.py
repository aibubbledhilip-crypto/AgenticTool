"""
Agentic AI Engine
Provides intelligent automation capabilities on top of DVSum APIs.
"""

import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import re


class TaskType(Enum):
    """Types of tasks the agentic engine can handle."""
    QUERY = "query"
    ANALYZE = "analyze"
    AUTOMATE = "automate"
    TROUBLESHOOT = "troubleshoot"
    REPORT = "report"
    DATA_QUALITY = "data_quality"
    CUSTOM = "custom"


@dataclass
class AgentTask:
    """Represents a task for the agentic engine."""
    task_type: TaskType
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    priority: int = 1


@dataclass
class AgentResult:
    """Result from an agentic operation."""
    success: bool
    task_type: TaskType
    result: Any
    actions_taken: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    error: Optional[str] = None


class AgenticEngine:
    """
    Agentic AI Engine that provides intelligent automation
    by orchestrating DVSum API calls and applying reasoning.
    """

    def __init__(self, dvsum_client):
        """
        Initialize the agentic engine.

        Args:
            dvsum_client: Initialized DVSumClient instance
        """
        self.client = dvsum_client
        self.conversation_history: List[Dict[str, str]] = []
        self.execution_log: List[Dict[str, Any]] = []

    def parse_intent(self, user_input: str) -> AgentTask:
        """
        Parse user input to determine intent and create a task.

        Args:
            user_input: Natural language input from user

        Returns:
            AgentTask with parsed intent
        """
        input_lower = user_input.lower()

        # Intent detection patterns
        query_patterns = ['show', 'get', 'list', 'find', 'search', 'what', 'display']
        analyze_patterns = ['analyze', 'examine', 'investigate', 'check', 'review']
        automate_patterns = ['automate', 'schedule', 'run', 'execute', 'trigger']
        troubleshoot_patterns = ['troubleshoot', 'diagnose', 'fix', 'debug', 'error', 'issue', 'problem']
        report_patterns = ['report', 'summary', 'summarize', 'dashboard', 'metrics']
        dq_patterns = ['data quality', 'dq', 'validation', 'quality check', 'anomaly']

        # Determine task type
        task_type = TaskType.CUSTOM
        if any(p in input_lower for p in dq_patterns):
            task_type = TaskType.DATA_QUALITY
        elif any(p in input_lower for p in troubleshoot_patterns):
            task_type = TaskType.TROUBLESHOOT
        elif any(p in input_lower for p in report_patterns):
            task_type = TaskType.REPORT
        elif any(p in input_lower for p in analyze_patterns):
            task_type = TaskType.ANALYZE
        elif any(p in input_lower for p in automate_patterns):
            task_type = TaskType.AUTOMATE
        elif any(p in input_lower for p in query_patterns):
            task_type = TaskType.QUERY

        # Extract parameters
        parameters = self._extract_parameters(user_input)

        return AgentTask(
            task_type=task_type,
            description=user_input,
            parameters=parameters,
            context={'conversation_history': self.conversation_history[-5:]}
        )

    def _extract_parameters(self, text: str) -> Dict[str, Any]:
        """Extract relevant parameters from text."""
        params = {}

        # Extract date ranges
        date_pattern = r'\b(\d{4}-\d{2}-\d{2})\b'
        dates = re.findall(date_pattern, text)
        if dates:
            params['dates'] = dates

        # Extract time periods
        time_periods = ['today', 'yesterday', 'last week', 'last month', 'this week', 'this month']
        for period in time_periods:
            if period in text.lower():
                params['time_period'] = period
                break

        # Extract numeric values
        number_pattern = r'\b(\d+)\b'
        numbers = re.findall(number_pattern, text)
        if numbers:
            params['numbers'] = [int(n) for n in numbers]

        return params

    def execute_task(self, task: AgentTask) -> AgentResult:
        """
        Execute an agentic task.

        Args:
            task: The task to execute

        Returns:
            AgentResult with execution results
        """
        actions_taken = []
        recommendations = []

        try:
            if task.task_type == TaskType.QUERY:
                result = self._handle_query(task, actions_taken)
            elif task.task_type == TaskType.ANALYZE:
                result = self._handle_analysis(task, actions_taken, recommendations)
            elif task.task_type == TaskType.AUTOMATE:
                result = self._handle_automation(task, actions_taken)
            elif task.task_type == TaskType.TROUBLESHOOT:
                result = self._handle_troubleshooting(task, actions_taken, recommendations)
            elif task.task_type == TaskType.REPORT:
                result = self._handle_report(task, actions_taken)
            elif task.task_type == TaskType.DATA_QUALITY:
                result = self._handle_data_quality(task, actions_taken, recommendations)
            else:
                result = self._handle_custom(task, actions_taken)

            # Log execution
            self.execution_log.append({
                'task': task.description,
                'type': task.task_type.value,
                'success': True,
                'actions': actions_taken
            })

            return AgentResult(
                success=True,
                task_type=task.task_type,
                result=result,
                actions_taken=actions_taken,
                recommendations=recommendations
            )

        except Exception as e:
            self.execution_log.append({
                'task': task.description,
                'type': task.task_type.value,
                'success': False,
                'error': str(e)
            })

            return AgentResult(
                success=False,
                task_type=task.task_type,
                result=None,
                actions_taken=actions_taken,
                error=str(e)
            )

    def _handle_query(self, task: AgentTask, actions: List[str]) -> Dict[str, Any]:
        """Handle query-type tasks."""
        actions.append("Analyzing query intent")

        # Use DVSum's natural language query capability
        actions.append("Executing natural language query via DVSum API")
        result = self.client.query_data(task.description)

        if not result.get('success'):
            # Fallback: try listing relevant resources
            actions.append("Query failed, attempting to list available agents")
            result = self.client.list_agents()

        return result

    def _handle_analysis(
        self,
        task: AgentTask,
        actions: List[str],
        recommendations: List[str]
    ) -> Dict[str, Any]:
        """Handle analysis-type tasks."""
        actions.append("Gathering data for analysis")

        # Get relevant data sources
        data_sources = self.client.list_data_sources()
        actions.append(f"Found {len(data_sources.get('data', []))} data sources")

        # Get analytics
        actions.append("Retrieving analytics data")
        analytics = self.client.get_analytics('usage')

        # Generate recommendations based on results
        recommendations.append("Review data quality scores regularly")
        recommendations.append("Consider automating repetitive analysis tasks")

        return {
            'data_sources': data_sources,
            'analytics': analytics,
            'summary': 'Analysis completed successfully'
        }

    def _handle_automation(self, task: AgentTask, actions: List[str]) -> Dict[str, Any]:
        """Handle automation-type tasks."""
        actions.append("Identifying automation target")

        # List existing workflows
        workflows = self.client.list_workflows()
        actions.append(f"Found {len(workflows.get('data', []))} existing workflows")

        # Check for matching workflow
        if workflows.get('success') and workflows.get('data'):
            actions.append("Evaluating existing workflows for match")

        return {
            'workflows': workflows,
            'message': 'Automation analysis complete. Ready to create or execute workflow.'
        }

    def _handle_troubleshooting(
        self,
        task: AgentTask,
        actions: List[str],
        recommendations: List[str]
    ) -> Dict[str, Any]:
        """Handle troubleshooting-type tasks."""
        actions.append("Initiating diagnostic process")

        results = {}

        # Check system health
        actions.append("Checking system health")
        health = self.client.health_check()
        results['health'] = health

        # Check for data quality issues
        actions.append("Scanning for data quality exceptions")
        dq_exceptions = self.client.get_dq_exceptions()
        results['dq_exceptions'] = dq_exceptions

        # Generate recommendations
        if dq_exceptions.get('data'):
            recommendations.append("Address data quality exceptions before proceeding")
        recommendations.append("Review recent system logs for additional context")
        recommendations.append("Consider running a full diagnostic workflow")

        return results

    def _handle_report(self, task: AgentTask, actions: List[str]) -> Dict[str, Any]:
        """Handle report-type tasks."""
        actions.append("Compiling report data")

        report_data = {}

        # Gather metrics
        actions.append("Gathering usage metrics")
        report_data['usage'] = self.client.get_analytics('usage')

        actions.append("Gathering performance metrics")
        report_data['performance'] = self.client.get_analytics('performance')

        # Get agent stats
        actions.append("Collecting agent statistics")
        report_data['agents'] = self.client.list_agents()

        # Get workflow stats
        actions.append("Collecting workflow statistics")
        report_data['workflows'] = self.client.list_workflows()

        return {
            'report': report_data,
            'generated_at': 'now',
            'summary': 'Report generated successfully'
        }

    def _handle_data_quality(
        self,
        task: AgentTask,
        actions: List[str],
        recommendations: List[str]
    ) -> Dict[str, Any]:
        """Handle data quality tasks."""
        actions.append("Initiating data quality assessment")

        results = {}

        # Get data sources
        actions.append("Fetching data sources")
        data_sources = self.client.list_data_sources()
        results['data_sources'] = data_sources

        # Get existing exceptions
        actions.append("Retrieving existing DQ exceptions")
        exceptions = self.client.get_dq_exceptions()
        results['exceptions'] = exceptions

        # Generate recommendations
        if exceptions.get('data'):
            recommendations.append(f"Found {len(exceptions.get('data', []))} DQ exceptions to review")
        recommendations.append("Schedule regular DQ checks for critical data sources")
        recommendations.append("Define custom DQ rules for business-specific validations")

        return results

    def _handle_custom(self, task: AgentTask, actions: List[str]) -> Dict[str, Any]:
        """Handle custom/unclassified tasks."""
        actions.append("Processing custom request")

        # Try to find the best agent to handle this
        actions.append("Searching for suitable agent")
        agents = self.client.list_agents()

        return {
            'message': 'Custom task processed',
            'available_agents': agents,
            'suggestion': 'You can create a custom workflow or agent for this task'
        }

    def process_message(self, message: str) -> Dict[str, Any]:
        """
        Main entry point for processing user messages.

        Args:
            message: User's natural language message

        Returns:
            Response with results and UI suggestions
        """
        # Add to conversation history
        self.conversation_history.append({
            'role': 'user',
            'content': message
        })

        # Parse intent and create task
        task = self.parse_intent(message)

        # Execute task
        result = self.execute_task(task)

        # Format response
        response = {
            'success': result.success,
            'task_type': result.task_type.value,
            'result': result.result,
            'actions_taken': result.actions_taken,
            'recommendations': result.recommendations,
            'error': result.error
        }

        # Add to conversation history
        self.conversation_history.append({
            'role': 'assistant',
            'content': json.dumps(response)
        })

        return response

    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get the execution history."""
        return self.execution_log

    def clear_history(self):
        """Clear conversation and execution history."""
        self.conversation_history = []
        self.execution_log = []
