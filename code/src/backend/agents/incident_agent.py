"""
Agent module for analyzing and resolving IT platform incidents.

This agent integrates with monitoring, service management, and knowledge base
systems to provide automated incident resolution capabilities.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import re

from .mocks.service_mocks import (
    MockMonitoringService,
    MockServiceManager,
    MockIncidentManager,
    MockKnowledgeBase
)


class ActionResult:
    """Results of an agent action."""
    
    def __init__(self, success: bool, output: str, error: Optional[str] = None):
        self.success = success
        self.output = output
        self.error = error
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "success": self.success,
            "output": self.output,
            "error": self.error
        }


class IncidentAgent:
    """Agent for analyzing and resolving IT platform incidents."""
    
    def __init__(self, incident_data: Dict[str, Any]):
        """Initialize with incident data."""
        self.incident = incident_data
        self.component = incident_data.get("component")
        self.issue_type = incident_data.get("title")
        self.severity = incident_data.get("severity", "medium")
        self.affected_service = incident_data.get("affected_service")
        
        # Initialize mock services
        # In a real implementation, these would be connections to actual services
        self.monitoring_service = MockMonitoringService()
        self.service_manager = MockServiceManager()
        self.incident_manager = MockIncidentManager()
        self.knowledge_base = MockKnowledgeBase()
        
        # Track actions performed
        self.actions_history = []
    
    def analyze_incident(self) -> Dict[str, Any]:
        """Analyze the incident and recommend actions."""
        # Get component health metrics
        component_health = self._get_component_health()
        
        # Find relevant KB articles
        kb_articles = self._find_relevant_kb_articles()
        
        # Get relevant historical incidents
        historical_incidents = self._find_similar_incidents()
        
        # Extract potential resolution steps from KB articles
        resolution_steps = self._extract_resolution_steps(kb_articles)
        
        # Map steps to executable actions
        executable_actions = self._map_steps_to_actions(resolution_steps)
        
        # Determine automation level
        automation_level = self._determine_automation_level(executable_actions)
        
        return {
            "incident_summary": self._generate_summary(),
            "component_health": component_health,
            "kb_articles": [
                {"id": article["id"], "title": article["title"]} 
                for article in kb_articles
            ],
            "recommended_actions": executable_actions,
            "automation_level": automation_level,
            "historical_incidents": historical_incidents
        }
    
    def execute_action(self, action_id: str, params: Optional[Dict[str, Any]] = None) -> ActionResult:
        """Execute a specific action related to incident resolution."""
        params = params or {}
        
        # Find the action in our recommended actions
        # In a real implementation, you'd probably store these in a database
        analysis = self.analyze_incident()
        actions = analysis.get("recommended_actions", [])
        
        target_action = None
        for action in actions:
            if action["id"] == action_id:
                target_action = action
                break
        
        if not target_action:
            return ActionResult(
                success=False,
                output="",
                error=f"Action {action_id} not found in recommended actions"
            )
        
        # Record the action regardless of outcome
        action_record = {
            "action_id": action_id,
            "action_type": target_action["action_type"],
            "description": target_action["description"],
            "timestamp": datetime.now().isoformat(),
            "params": params
        }
        
        # Execute the action based on its type
        result = None
        
        try:
            if target_action["action_type"] == "restart":
                result = self._execute_restart_action(params)
            elif target_action["action_type"] == "scale":
                result = self._execute_scale_action(params)
            elif target_action["action_type"] == "update_config":
                result = self._execute_update_config_action(params)
            elif target_action["action_type"] == "diagnostic":
                result = self._execute_diagnostic_action(params)
            else:
                result = ActionResult(
                    success=False,
                    output="",
                    error=f"Unsupported action type: {target_action['action_type']}"
                )
        except Exception as e:
            result = ActionResult(
                success=False,
                output="",
                error=f"Error executing action: {str(e)}"
            )
        
        # Update action record with result
        action_record["result"] = result.to_dict()
        self.actions_history.append(action_record)
        
        # If incident_id is provided, add the action to the incident
        if "incident_id" in params:
            self.incident_manager.add_incident_action(
                params["incident_id"],
                target_action["description"],
                result.to_dict()
            )
        
        return result
    
    def run_health_check(self) -> Dict[str, Any]:
        """Run automated health check for affected component."""
        if not self.component:
            return {"error": "No component specified"}
        
        # Get basic service info
        service_info = self.service_manager.get_service_info(self.component)
        
        # Get monitoring metrics
        metrics = {}
        
        if self.component == "api-gateway":
            metrics["cpu_usage"] = self._get_metric("cpu_usage")
            metrics["memory_usage"] = self._get_metric("memory_usage")
            metrics["request_rate"] = self._get_metric("request_rate")
            metrics["error_rate"] = self._get_metric("error_rate")
            metrics["response_time_ms"] = self._get_metric("response_time_ms")
        
        elif self.component == "database":
            metrics["cpu_usage"] = self._get_metric("cpu_usage")
            metrics["memory_usage"] = self._get_metric("memory_usage")
            metrics["connection_pool.used"] = self._get_metric("connection_pool.used")
            metrics["connection_pool.max"] = self._get_metric("connection_pool.max")
            metrics["active_queries"] = self._get_metric("active_queries")
            metrics["query_execution_time_ms"] = self._get_metric("query_execution_time_ms")
        
        elif self.component == "message-queue":
            metrics["cpu_usage"] = self._get_metric("cpu_usage")
            metrics["memory_usage"] = self._get_metric("memory_usage")
            metrics["queue_depth"] = self._get_metric("queue_depth")
            metrics["consumer_lag"] = self._get_metric("consumer_lag")
            metrics["publish_rate"] = self._get_metric("publish_rate")
            metrics["consume_rate"] = self._get_metric("consume_rate")
        
        # Get recent logs
        logs_result = self.service_manager.execute_command(
            self.component, "logs", {"lines": 20}
        )
        
        logs = logs_result.get("output", "") if logs_result.get("success", False) else "Unable to retrieve logs"
        
        # Determine health status based on metrics
        health_status = self._determine_health_status(metrics)
        
        return {
            "component": self.component,
            "status": health_status,
            "service_info": service_info,
            "metrics": metrics,
            "logs": logs,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_action_history(self) -> List[Dict[str, Any]]:
        """Get history of actions performed by this agent."""
        return self.actions_history
    
    def _get_component_health(self) -> Dict[str, Any]:
        """Get health metrics for the component."""
        return self.run_health_check()
    
    def _find_relevant_kb_articles(self) -> List[Dict[str, Any]]:
        """Find knowledge base articles relevant to this incident."""
        # First try with component and issue type
        if self.component and self.issue_type:
            # Extract the main issue from the title if possible
            issue_keywords = self.issue_type.lower()
            articles = self.knowledge_base.search_articles(issue_keywords, self.component)
            if articles:
                return articles
        
        # Try with just the component
        if self.component:
            articles = self.knowledge_base.get_articles_by_component(self.component)
            if articles:
                return articles
        
        # Try with general search in description
        if "description" in self.incident:
            articles = self.knowledge_base.search_articles(self.incident["description"])
            if articles:
                return articles
        
        return []
    
    def _find_similar_incidents(self) -> List[Dict[str, Any]]:
        """Find similar historical incidents."""
        # In a real implementation, this would use more sophisticated similarity matching
        if self.component:
            return self.incident_manager.list_incidents(component=self.component)
        return []
    
    def _extract_resolution_steps(self, kb_articles: List[Dict[str, Any]]) -> List[str]:
        """Extract resolution steps from KB articles."""
        if not kb_articles:
            return self._get_default_resolution_steps()
        
        # Get the most relevant article
        article_id = kb_articles[0]["id"]
        article = self.knowledge_base.get_article(article_id)
        
        if not article or "content" not in article:
            return self._get_default_resolution_steps()
        
        # Extract steps from the article content
        steps = []
        in_resolution_section = False
        
        for line in article["content"].split("\n"):
            if "## Resolution Steps" in line:
                in_resolution_section = True
                continue
            elif in_resolution_section and line.startswith("##"):
                # We've hit the next section
                break
            
            if in_resolution_section and line.strip().startswith("###"):
                # This is a step header
                step = line.strip().replace("### ", "")
                steps.append(step)
        
        return steps if steps else self._get_default_resolution_steps()
    
    def _get_default_resolution_steps(self) -> List[str]:
        """Get default resolution steps when no KB article is found."""
        if self.component == "api-gateway":
            return [
                "1. Check API Gateway metrics",
                "2. Review recent configuration changes",
                "3. Restart API Gateway service",
                "4. Scale API Gateway resources if needed",
                "5. Implement rate limiting"
            ]
        elif self.component == "database":
            return [
                "1. Check database connection pool",
                "2. Identify long-running queries",
                "3. Adjust connection pool size",
                "4. Set connection timeouts",
                "5. Monitor for improvement"
            ]
        elif self.component == "message-queue":
            return [
                "1. Check queue depth and consumer lag",
                "2. Identify bottlenecks in processing",
                "3. Scale up consumers",
                "4. Optimize message processing",
                "5. Monitor for improvement"
            ]
        else:
            return [
                "1. Check component health",
                "2. Review logs for errors",
                "3. Restart service if needed",
                "4. Adjust resource allocation",
                "5. Monitor for improvement"
            ]
    
    def _map_steps_to_actions(self, steps: List[str]) -> List[Dict[str, Any]]:
        """Map textual steps to executable actions."""
        actions = []
        
        for i, step in enumerate(steps):
            action_type = self._determine_action_type(step)
            action = {
                "id": f"action_{i}",
                "description": step,
                "action_type": action_type,
                "requires_approval": action_type in ["restart", "scale", "update_config"],
                "params": self._extract_action_params(step, action_type)
            }
            actions.append(action)
        
        return actions
    
    def _determine_action_type(self, step: str) -> str:
        """Map resolution step to action type."""
        step_lower = step.lower()
        
        # Check for restart actions
        if "restart" in step_lower or "reboot" in step_lower:
            return "restart"
        
        # Check for scaling actions
        if "scale" in step_lower or "add instance" in step_lower or "increase capacity" in step_lower:
            return "scale"
        
        # Check for configuration update actions
        if "adjust" in step_lower or "configure" in step_lower or "set" in step_lower or "update config" in step_lower:
            return "update_config"
        
        # Check for diagnostic actions
        if any(word in step_lower for word in ["check", "review", "analyze", "monitor", "identify"]):
            return "diagnostic"
        
        # Default to other
        return "other"
    
    def _extract_action_params(self, step: str, action_type: str) -> Dict[str, Any]:
        """Extract parameters from step description based on action type."""
        params = {}
        step_lower = step.lower()
        
        if action_type == "scale":
            # Try to extract scaling amount
            scale_match = re.search(r"scale\s+\w+\s+(\d+)", step_lower)
            if scale_match:
                params["amount"] = int(scale_match.group(1))
            else:
                # Default scaling
                params["amount"] = 2
        
        elif action_type == "update_config":
            # Look for configuration parameters
            if self.component == "database" and "connection pool" in step_lower:
                # Extract connection pool size if mentioned
                pool_match = re.search(r"(\d+)", step_lower)
                if pool_match:
                    value = int(pool_match.group(1))
                    params["config"] = {"max_connections": value}
                else:
                    # Default increase
                    params["config"] = {"max_connections": 300}  # Up from 200
            
            elif self.component == "api-gateway" and "rate limit" in step_lower:
                # Extract rate limit if mentioned
                rate_match = re.search(r"(\d+)\s*r(eq)?", step_lower)
                if rate_match:
                    value = int(rate_match.group(1))
                    params["config"] = {"rate_limit": value}
                else:
                    # Default rate limit
                    params["config"] = {"rate_limit": 2000}  # Up from 1000
        
        return params
    
    def _determine_automation_level(self, actions: List[Dict[str, Any]]) -> str:
        """Determine how much can be automated."""
        if not actions:
            return "manual"
        
        # Count actions that require approval
        approval_count = sum(1 for action in actions if action.get("requires_approval", True))
        
        # If no actions require approval, it's fully automatable
        if approval_count == 0:
            return "fully-automated"
        
        # If all actions require approval, it's manual
        if approval_count == len(actions):
            return "manual"
        
        # Otherwise, it's semi-automated
        return "semi-automated"
    
    def _generate_summary(self) -> str:
        """Generate incident summary."""
        return f"{self.issue_type} affecting {self.component} - {self.severity.upper()} severity"
    
    def _execute_restart_action(self, params: Dict[str, Any]) -> ActionResult:
        """Execute a restart action."""
        if not self.component:
            return ActionResult(
                success=False,
                output="",
                error="No component specified for restart"
            )
        
        # Execute restart command
        result = self.service_manager.execute_command(self.component, "restart")
        
        if result.get("success", False):
            # Update monitoring service to reflect improvement
            if self.component == "api-gateway":
                self.monitoring_service.update_state(self.component, {
                    "cpu_usage": 45,  # Reduced from 87
                    "error_rate": 1.2,  # Reduced from 8.2
                    "status": "healthy"
                })
            elif self.component == "database":
                self.monitoring_service.update_state(self.component, {
                    "connection_pool.used": 90,  # Reduced from 180
                    "connection_pool.wait_time_ms": 50,  # Reduced from 250
                    "status": "healthy"
                })
            
            return ActionResult(
                success=True,
                output=result.get("output", "Service restarted successfully")
            )
        else:
            return ActionResult(
                success=False,
                output="",
                error=result.get("error", "Unknown error restarting service")
            )
    
    def _execute_scale_action(self, params: Dict[str, Any]) -> ActionResult:
        """Execute a scaling action."""
        if not self.component:
            return ActionResult(
                success=False,
                output="",
                error="No component specified for scaling"
            )
        
        amount = params.get("amount", 1)
        
        # Execute scale command
        result = self.service_manager.execute_command(
            self.component,
            "scale",
            {"amount": amount}
        )
        
        if result.get("success", False):
            # Update monitoring service to reflect improvement
            if self.component == "api-gateway":
                # Scale up generally improves CPU and response time
                self.monitoring_service.update_state(self.component, {
                    "cpu_usage": max(30, 87 / (1 + amount * 0.5)),  # Reduced based on scale
                    "response_time_ms": max(100, 350 / (1 + amount * 0.3)),  # Reduced based on scale
                    "status": "healthy"
                })
            elif self.component == "message-queue":
                # Scaling consumers improves queue metrics
                self.monitoring_service.update_state(self.component, {
                    "queue_depth": max(1000, 10500 / (1 + amount * 0.4)),  # Reduced based on scale
                    "consumer_lag": max(500, 3200 / (1 + amount * 0.4)),  # Reduced based on scale
                    "status": "healthy"
                })
            
            return ActionResult(
                success=True,
                output=result.get("output", f"Service scaled by {amount} instances")
            )
        else:
            return ActionResult(
                success=False,
                output="",
                error=result.get("error", "Unknown error scaling service")
            )
    
    def _execute_update_config_action(self, params: Dict[str, Any]) -> ActionResult:
        """Execute a configuration update action."""
        if not self.component:
            return ActionResult(
                success=False,
                output="",
                error="No component specified for configuration update"
            )
        
        config = params.get("config", {})
        if not config:
            return ActionResult(
                success=False,
                output="",
                error="No configuration updates specified"
            )
        
        # Execute update config command
        result = self.service_manager.execute_command(
            self.component,
            "update_config",
            {"config": config}
        )
        
        if result.get("success", False):
            # Update monitoring service to reflect improvement
            if self.component == "database" and "max_connections" in config:
                # Update connection pool max
                self.monitoring_service.update_state(self.component, {
                    "connection_pool.max": config["max_connections"],
                    "connection_pool.wait_time_ms": 30,  # Reduced from 250
                    "status": "healthy"
                })
            elif self.component == "api-gateway" and "rate_limit" in config:
                # Update rate limiting
                self.monitoring_service.update_state(self.component, {
                    "error_rate": 0.5,  # Reduced from 8.2
                    "status": "healthy"
                })
            
            return ActionResult(
                success=True,
                output=result.get("output", "Configuration updated successfully")
            )
        else:
            return ActionResult(
                success=False,
                output="",
                error=result.get("error", "Unknown error updating configuration")
            )
    
    def _execute_diagnostic_action(self, params: Dict[str, Any]) -> ActionResult:
        """Execute a diagnostic action."""
        # Run health check
        health_data = self.run_health_check()
        
        # Extract relevant metrics based on component
        metrics_output = []
        if self.component == "api-gateway":
            metrics_output = [
                f"CPU Usage: {health_data['metrics'].get('cpu_usage', {}).get('current', 'N/A')}%",
                f"Memory Usage: {health_data['metrics'].get('memory_usage', {}).get('current', 'N/A')}%",
                f"Request Rate: {health_data['metrics'].get('request_rate', {}).get('current', 'N/A')} req/s",
                f"Error Rate: {health_data['metrics'].get('error_rate', {}).get('current', 'N/A')}%",
                f"Response Time: {health_data['metrics'].get('response_time_ms', {}).get('current', 'N/A')} ms"
            ]
        elif self.component == "database":
            metrics_output = [
                f"CPU Usage: {health_data['metrics'].get('cpu_usage', {}).get('current', 'N/A')}%",
                f"Memory Usage: {health_data['metrics'].get('memory_usage', {}).get('current', 'N/A')}%",
                f"Connection Pool: {health_data['metrics'].get('connection_pool.used', {}).get('current', 'N/A')}/{health_data['metrics'].get('connection_pool.max', {}).get('current', 'N/A')}",
                f"Active Queries: {health_data['metrics'].get('active_queries', {}).get('current', 'N/A')}",
                f"Query Time: {health_data['metrics'].get('query_execution_time_ms', {}).get('current', 'N/A')} ms"
            ]
        elif self.component == "message-queue":
            metrics_output = [
                f"CPU Usage: {health_data['metrics'].get('cpu_usage', {}).get('current', 'N/A')}%",
                f"Memory Usage: {health_data['metrics'].get('memory_usage', {}).get('current', 'N/A')}%",
                f"Queue Depth: {health_data['metrics'].get('queue_depth', {}).get('current', 'N/A')}",
                f"Consumer Lag: {health_data['metrics'].get('consumer_lag', {}).get('current', 'N/A')}",
                f"Publish Rate: {health_data['metrics'].get('publish_rate', {}).get('current', 'N/A')} msg/s",
                f"Consume Rate: {health_data['metrics'].get('consume_rate', {}).get('current', 'N/A')} msg/s"
            ]
        
        # Extract log patterns
        logs = health_data.get("logs", "")
        error_count = logs.lower().count("error")
        warn_count = logs.lower().count("warn")
        
        diagnostic_output = "\n".join([
            f"Diagnostic results for {self.component}:",
            f"Status: {health_data.get('status', 'Unknown')}",
            "---",
            "Key Metrics:",
            *metrics_output,
            "---",
            f"Log Analysis: Found {error_count} errors and {warn_count} warnings in recent logs."
        ])
        
        return ActionResult(
            success=True,
            output=diagnostic_output
        )
    
    def _determine_health_status(self, metrics: Dict[str, Any]) -> str:
        """Determine component health status based on metrics."""
        # Check for critical metrics based on component type
        if self.component == "api-gateway":
            cpu = metrics.get("cpu_usage", {}).get("current", 0)
            error_rate = metrics.get("error_rate", {}).get("current", 0)
            
            if cpu > 80 or error_rate > 5:
                return "critical"
            elif cpu > 60 or error_rate > 2:
                return "warning"
            else:
                return "healthy"
        
        elif self.component == "database":
            conn_used = metrics.get("connection_pool.used", {}).get("current", 0)
            conn_max = metrics.get("connection_pool.max", {}).get("current", 1)
            
            usage_percent = (conn_used / conn_max * 100) if conn_max else 0
            
            if usage_percent > 90:
                return "critical"
            elif usage_percent > 70:
                return "warning"
            else:
                return "healthy"
        
        elif self.component == "message-queue":
            queue_depth = metrics.get("queue_depth", {}).get("current", 0)
            
            if queue_depth > 10000:
                return "critical"
            elif queue_depth > 5000:
                return "warning"
            else:
                return "healthy"
        
        # Default for unknown components
        return "unknown"
    
    def _get_metric(self, metric_name: str) -> Dict[str, Any]:
        """Get a specific metric from the monitoring service."""
        result = self.monitoring_service.query(
            metric=metric_name,
            filter={"service": self.component}
        )
        
        if result.get("status") == "error":
            return {"current": "N/A", "error": result.get("error")}
        
        return result 