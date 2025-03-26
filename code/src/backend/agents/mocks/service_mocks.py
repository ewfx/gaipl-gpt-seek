"""
Mock services for simulating IT infrastructure components and services.

These mock services provide simulated data and responses for different IT components
that would normally be accessed via APIs or direct connections in a real environment.
They allow demonstrating agent functionality without requiring actual infrastructure.
"""

from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
import random
import time
import json
from ...utils.constants import MOCK_KB_ARTICLES, MONITORING_SERVICES_MOCK_STATE, MOCK_SERVICES


class MockMonitoringService:
    """Mock service for monitoring APIs (like Prometheus, Datadog, New Relic, etc.)"""
    
    def __init__(self, initial_state: Dict[str, Any] = None):
        """Initialize with an optional initial state, otherwise use defaults"""
        self.state = initial_state or MONITORING_SERVICES_MOCK_STATE
        # Keep history for trending
        self.history = {component: [] for component in self.state}
        # Generate some historical data points
        self._initialize_history()
    
    def _initialize_history(self):
        """Generate mock historical data for trending"""
        for component in self.state:
            # Create 24 hourly data points (1 day of history)
            for i in range(24):
                timestamp = datetime.now() - timedelta(hours=24-i)
                # Copy current state but add some variance
                point = {}
                for metric, value in self.state[component].items():
                    if isinstance(value, dict):
                        continue  # Skip nested structures for history
                    if isinstance(value, (int, float)) and metric != "status":
                        # Add randomness within ±15%
                        variance = random.uniform(-0.15, 0.15)
                        point[metric] = value * (1 + variance)
                    else:
                        point[metric] = value
                
                self.history[component].append({
                    "timestamp": timestamp.isoformat(),
                    "metrics": point
                })
    
    def query(self, metric: str, filter: Dict[str, str], timeframe: str = "last_15m") -> Dict[str, Any]:
        """Simulate querying metrics from a monitoring service"""
        component = filter.get("service", "")
        
        if component not in self.state:
            return {"error": "Component not found", "status": "error"}
        
        # Handle nested metrics with dot notation (e.g., "connection_pool.used")
        if "." in metric:
            parts = metric.split(".")
            current = self.state[component]
            for part in parts:
                if part not in current:
                    return {"error": f"Metric {metric} not found", "status": "error"}
                current = current[part]
            value = current
        else:
            # Handle simple metrics
            if metric not in self.state[component]:
                return {"error": f"Metric {metric} not found", "status": "error"}
            value = self.state[component][metric]
        
        # For numeric metrics, provide statistical information
        if isinstance(value, (int, float)):
            # Calculate timeframe in minutes
            minutes = 15  # default
            if timeframe.startswith("last_"):
                time_spec = timeframe[5:]
                if time_spec.endswith("m"):
                    minutes = int(time_spec[:-1])
                elif time_spec.endswith("h"):
                    minutes = int(time_spec[:-1]) * 60
                elif time_spec.endswith("d"):
                    minutes = int(time_spec[:-1]) * 60 * 24
            
            # Generate some reasonable min/max/avg values
            # More variance for longer timeframes
            variance_factor = min(0.3, minutes / 60)
            min_val = value * (1 - random.uniform(0, variance_factor))
            max_val = value * (1 + random.uniform(0, variance_factor))
            avg_val = (min_val + max_val + value) / 3
            
            return {
                "current": value,
                "avg": avg_val,
                "max": max_val,
                "min": min_val,
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }
        
        # For non-numeric values, just return the current state
        return {
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }
    
    def get_history(self, component: str, metric: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get historical values for a metric"""
        if component not in self.history:
            return {"error": "Component history not found"}
        
        # Return the historical data for the specified timeframe
        now = datetime.now()
        cutoff = now - timedelta(hours=hours)
        
        result = []
        for point in self.history[component]:
            timestamp = datetime.fromisoformat(point["timestamp"])
            if timestamp >= cutoff:
                if metric in point["metrics"]:
                    result.append({
                        "timestamp": point["timestamp"],
                        "value": point["metrics"][metric]
                    })
        
        return result
        
    def update_state(self, component: str, updates: Dict[str, Any]) -> bool:
        """Update the mock state (simulates remediation effects)"""
        if component not in self.state:
            return False
        
        # Update the state
        if isinstance(updates, dict):
            # Handle nested updates with dot notation
            for key, value in updates.items():
                if "." in key:
                    parts = key.split(".")
                    current = self.state[component]
                    for part in parts[:-1]:
                        if part not in current:
                            current[part] = {}
                        current = current[part]
                    current[parts[-1]] = value
                else:
                    self.state[component][key] = value
            
            # Add a new history point with updated values
            point = {}
            for metric, value in self.state[component].items():
                if isinstance(value, dict):
                    continue  # Skip nested structures for history
                point[metric] = value
            
            self.history[component].append({
                "timestamp": datetime.now().isoformat(),
                "metrics": point
            })
            
            return True
        
        return False


class MockServiceManager:
    """Mock service for executing commands on services and infrastructure"""
    
    def __init__(self):
        """Initialize the service manager with a mock service inventory"""
        self.services = MOCK_SERVICES
        
        # Keep command history
        self.command_history = []
    
    def get_service_info(self, service: str) -> Dict[str, Any]:
        """Get information about a service"""
        if service not in self.services:
            return {"error": "Service not found", "status": "error"}
        
        return self.services[service]
    
    def execute_command(self, service: str, command: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Simulate executing a command on a service"""
        params = params or {}
        
        if service not in self.services:
            return {
                "success": False,
                "output": "",
                "error": f"Service {service} not found",
                "exit_code": 1
            }
        
        # Record the command in history
        self.command_history.append({
            "timestamp": datetime.now().isoformat(),
            "service": service,
            "command": command,
            "params": params
        })
        
        # Simulate command execution time
        time.sleep(0.5)
        
        # Process different commands
        if command == "restart":
            return self._handle_restart(service, params)
        elif command == "scale":
            return self._handle_scale(service, params)
        elif command == "update_config":
            return self._handle_update_config(service, params)
        elif command == "status":
            return self._handle_status(service, params)
        elif command == "logs":
            return self._handle_logs(service, params)
        
        return {
            "success": False,
            "output": "",
            "error": f"Unknown command {command}",
            "exit_code": 1
        }
    
    def _handle_restart(self, service: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the restart command"""
        # Simulate service being temporarily down during restart
        self.services[service]["status"] = "restarting"
        
        # Simulate restart time
        time.sleep(1)
        
        # Service is back up
        self.services[service]["status"] = "running"
        
        return {
            "success": True,
            "output": f"Service {service} restarted successfully",
            "exit_code": 0
        }
    
    def _handle_scale(self, service: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the scale command"""
        amount = params.get("amount", 1)
        current = self.services[service]["instances"]
        
        if amount <= 0 and current + amount <= 0:
            return {
                "success": False,
                "output": "",
                "error": f"Cannot scale {service} below 1 instance",
                "exit_code": 1
            }
        
        # Update the instance count
        self.services[service]["instances"] = current + amount
        
        scale_type = "up" if amount > 0 else "down"
        return {
            "success": True,
            "output": f"Scaled {service} {scale_type} by {abs(amount)} instances. New count: {self.services[service]['instances']}",
            "exit_code": 0
        }
    
    def _handle_update_config(self, service: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the update_config command"""
        config_updates = params.get("config", {})
        
        if not config_updates:
            return {
                "success": False,
                "output": "",
                "error": "No configuration updates provided",
                "exit_code": 1
            }
        
        # Update the configuration
        for key, value in config_updates.items():
            if key in self.services[service]["config"]:
                self.services[service]["config"][key] = value
        
        return {
            "success": True,
            "output": f"Configuration for {service} updated successfully: {json.dumps(config_updates)}",
            "exit_code": 0
        }
    
    def _handle_status(self, service: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the status command"""
        return {
            "success": True,
            "output": f"Service: {service}\nStatus: {self.services[service]['status']}\nVersion: {self.services[service]['version']}\nInstances: {self.services[service]['instances']}",
            "exit_code": 0
        }
    
    def _handle_logs(self, service: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the logs command"""
        lines = params.get("lines", 10)
        
        # Generate some fake logs
        log_entries = []
        now = datetime.now()
        log_types = ["INFO", "DEBUG", "WARN", "ERROR"]
        
        for i in range(lines):
            timestamp = now - timedelta(seconds=i*10)
            log_type = log_types[0] if i > lines*0.9 else random.choice(log_types)
            
            if service == "api-gateway":
                log_entries.append(f"{timestamp.isoformat()} {log_type} [Gateway-{i%3}] Processing request from client 192.168.1.{random.randint(1, 255)}")
            elif service == "database":
                log_entries.append(f"{timestamp.isoformat()} {log_type} [DB-Main] Query execution time: {random.randint(10, 500)}ms, connections: {random.randint(100, 190)}")
            elif service == "message-queue":
                log_entries.append(f"{timestamp.isoformat()} {log_type} [MQ-{i%2}] Message batch processed, size: {random.randint(10, 100)}, time: {random.randint(5, 150)}ms")
            else:
                log_entries.append(f"{timestamp.isoformat()} {log_type} [{service.capitalize()}] Generic log entry {i}")
        
        return {
            "success": True,
            "output": "\n".join(log_entries),
            "exit_code": 0
        }
    
    def get_command_history(self, service: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get history of commands executed on services"""
        if service is None:
            return self.command_history
        
        return [cmd for cmd in self.command_history if cmd["service"] == service]


class MockIncidentManager:
    """Mock service for managing incidents and alerts"""
    
    def __init__(self):
        """Initialize with some mock incidents"""
        self.incidents = []
        self.alerts = []
        self.incident_counter = 0
        self.alert_counter = 0
        
        # Create some initial incidents
        self._create_initial_incidents()
    
    def _create_initial_incidents(self):
        """Create some initial incidents"""
        self.create_incident(
            title="API Gateway High CPU Usage",
            component="api-gateway",
            severity="high",
            description="API Gateway showing sustained high CPU usage above 85%. Response times degraded.",
            affected_service="Data Analytics"
        )
        
        self.create_incident(
            title="Database Connection Pool Exhaustion",
            component="database",
            severity="high",
            description="Database connection pool near capacity (180/200). Query wait times increasing.",
            affected_service="User Authentication"
        )
        
        self.create_incident(
            title="Message Queue Backup",
            component="message-queue",
            severity="medium",
            description="Message queue depth exceeding 10K messages with consumer lag growing. Processing delay risk.",
            affected_service="Order Processing"
        )
    
    def create_incident(self, title: str, component: str, severity: str, 
                       description: str, affected_service: str) -> Dict[str, Any]:
        """Create a new incident"""
        self.incident_counter += 1
        incident_id = f"INC{self.incident_counter:06d}"
        
        incident = {
            "id": incident_id,
            "title": title,
            "component": component,
            "severity": severity,
            "description": description,
            "affected_service": affected_service,
            "status": "open",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "assigned_to": None,
            "actions": [],
            "resolution": None
        }
        
        self.incidents.append(incident)
        return incident
    
    def update_incident(self, incident_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an incident"""
        for i, incident in enumerate(self.incidents):
            if incident["id"] == incident_id:
                for key, value in updates.items():
                    if key in incident:
                        incident[key] = value
                
                incident["updated_at"] = datetime.now().isoformat()
                self.incidents[i] = incident
                return incident
        
        return None
    
    def add_incident_action(self, incident_id: str, action: str, result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Add an action to an incident's history"""
        for incident in self.incidents:
            if incident["id"] == incident_id:
                action_entry = {
                    "action": action,
                    "timestamp": datetime.now().isoformat(),
                    "result": result
                }
                
                incident["actions"].append(action_entry)
                incident["updated_at"] = datetime.now().isoformat()
                return incident
        
        return None
    
    def resolve_incident(self, incident_id: str, resolution: str) -> Optional[Dict[str, Any]]:
        """Mark an incident as resolved"""
        for incident in self.incidents:
            if incident["id"] == incident_id:
                incident["status"] = "resolved"
                incident["resolution"] = resolution
                incident["resolved_at"] = datetime.now().isoformat()
                incident["updated_at"] = datetime.now().isoformat()
                return incident
        
        return None
    
    def get_incident(self, incident_id: str) -> Optional[Dict[str, Any]]:
        """Get an incident by ID"""
        for incident in self.incidents:
            if incident["id"] == incident_id:
                return incident
        
        return None
    
    def list_incidents(self, status: Optional[str] = None, component: Optional[str] = None) -> List[Dict[str, Any]]:
        """List incidents with optional filters"""
        result = self.incidents
        
        if status is not None:
            result = [incident for incident in result if incident["status"] == status]
        
        if component is not None:
            result = [incident for incident in result if incident["component"] == component]
        
        return sorted(result, key=lambda x: x["created_at"], reverse=True)
    
    def create_alert(self, title: str, component: str, severity: str, message: str) -> Dict[str, Any]:
        """Create a new alert"""
        self.alert_counter += 1
        alert_id = f"ALT{self.alert_counter:06d}"
        
        alert = {
            "id": alert_id,
            "title": title,
            "component": component,
            "severity": severity,
            "message": message,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "acknowledged": False
        }
        
        self.alerts.append(alert)
        return alert
    
    def acknowledge_alert(self, alert_id: str) -> Optional[Dict[str, Any]]:
        """Acknowledge an alert"""
        for i, alert in enumerate(self.alerts):
            if alert["id"] == alert_id:
                alert["acknowledged"] = True
                alert["acknowledged_at"] = datetime.now().isoformat()
                self.alerts[i] = alert
                return alert
        
        return None
    
    def list_alerts(self, component: Optional[str] = None, acknowledged: Optional[bool] = None) -> List[Dict[str, Any]]:
        """List alerts with optional filters"""
        result = self.alerts
        
        if component is not None:
            result = [alert for alert in result if alert["component"] == component]
        
        if acknowledged is not None:
            result = [alert for alert in result if alert["acknowledged"] == acknowledged]
        
        return sorted(result, key=lambda x: x["created_at"], reverse=True)


class MockKnowledgeBase:
    """Mock service for knowledge base articles and remediation guides"""
    
    def __init__(self):
        """Initialize with mock KB articles"""
        self.kb_articles = MOCK_KB_ARTICLES
    
    def get_article(self, article_id: str) -> Optional[Dict[str, Any]]:
        """Get a knowledge base article by ID"""
        for article in self.kb_articles:
            if article["id"] == article_id:
                return article
        
        return None
    
    def search_articles(self, query: str, component: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search knowledge base articles"""
        query = query.lower()
        results = []
        
        for article in self.kb_articles:
            # Check if component filter matches
            if component is not None and article["component"] != component:
                continue
            
            # Simple search in title and content
            if (query in article["title"].lower() or 
                query in article["content"].lower() or 
                query in article["issue_type"].lower()):
                
                # Add a relevance score based on where the match was found
                score = 0
                if query in article["title"].lower():
                    score += 3
                if query in article["issue_type"].lower():
                    score += 2
                if query in article["content"].lower():
                    score += 1
                
                # Include only essential info in search results
                results.append({
                    "id": article["id"],
                    "title": article["title"],
                    "component": article["component"],
                    "issue_type": article["issue_type"],
                    "relevance_score": score
                })
        
        # Sort by relevance score
        return sorted(results, key=lambda x: x["relevance_score"], reverse=True)
    
    def get_articles_by_component(self, component: str) -> List[Dict[str, Any]]:
        """Get all KB articles for a specific component"""
        return [
            {
                "id": article["id"],
                "title": article["title"],
                "issue_type": article["issue_type"]
            }
            for article in self.kb_articles
            if article["component"] == component
        ] 