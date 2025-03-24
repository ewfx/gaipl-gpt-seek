import random
import json

# Common IT components and issues
COMPONENTS = [
    "Database", "API Gateway", "Load Balancer", "Authentication Service",
    "Message Queue", "Cache Service", "Web Server", "Kubernetes Cluster",
    "Monitoring System", "Logging Service"
]

ISSUES = {
    "Database": [
        "High CPU Usage",
        "Connection Pool Exhaustion",
        "Slow Query Performance",
        "Replication Lag",
        "Storage Space Critical"
    ],
    "API Gateway": [
        "Rate Limiting Errors",
        "Invalid Route Configuration",
        "High Latency",
        "SSL Certificate Expiration",
        "Authentication Failures"
    ],
    "Load Balancer": [
        "Health Check Failures",
        "Connection Timeouts",
        "SSL Handshake Errors",
        "Backend Pool Degradation",
        "Configuration Sync Issues"
    ],
    "Authentication Service": [
        "Token Validation Errors",
        "LDAP Sync Failure",
        "High Authentication Latency",
        "Session Management Issues",
        "Certificate Chain Errors"
    ],
    "Message Queue": [
        "Queue Backup",
        "Consumer Group Lag",
        "Broker Connectivity Issues",
        "Message Processing Delays",
        "Storage Capacity Alerts"
    ]
}

RESOLUTION_TEMPLATES = [
    [
        "1. Identify affected {component} instances",
        "2. Review system metrics and logs",
        "3. {specific_action}",
        "4. Validate service restoration",
        "5. Document findings in post-mortem"
    ],
    [
        "1. Check {component} health status",
        "2. Analyze recent changes and deployments",
        "3. {specific_action}",
        "4. Test functionality",
        "5. Update runbook with findings"
    ],
    [
        "1. Assess impact on dependent services",
        "2. Review {component} configuration",
        "3. {specific_action}",
        "4. Implement preventive measures",
        "5. Update monitoring thresholds"
    ]
]

SPECIFIC_ACTIONS = {
    "High CPU Usage": "Scale up resources or optimize queries",
    "Connection Pool Exhaustion": "Adjust pool size and timeout settings",
    "Slow Query Performance": "Analyze and optimize query execution plans",
    "Rate Limiting Errors": "Adjust rate limit thresholds and policies",
    "Health Check Failures": "Verify backend service health and connectivity",
    "Token Validation Errors": "Review token configuration and key rotation",
    "Queue Backup": "Scale consumers and clear backlog"
}

def generate_kb_link(component, issue):
    """Generate a realistic-looking knowledge base article link."""
    kb_id = random.randint(10000, 99999)
    sanitized_issue = issue.lower().replace(" ", "-")
    return f"https://support.platform.company.com/kb/articles/{kb_id}-resolving-{sanitized_issue}-in-{component.lower()}"

def generate_incident_description(component, issue):
    """Generate a detailed incident description."""
    impact_levels = ["Critical", "High", "Medium", "Low"]
    services = ["Customer Portal", "Internal Tools", "Payment Processing", "Data Analytics", "User Authentication"]
    affected_service = random.choice(services)
    impact = random.choice(impact_levels)
    
    return f"""Impact Level: {impact}
Affected Service: {affected_service}
Component: {component}
Issue: {issue}

Multiple users reported {issue.lower()} in the {component} system. This is affecting {affected_service} functionality.
Initial investigation shows potential {random.choice(['configuration', 'resource', 'network', 'system'])} issues.
Immediate attention required to prevent service degradation."""

def generate_resolution_steps(component, issue):
    """Generate detailed resolution steps."""
    template = random.choice(RESOLUTION_TEMPLATES)
    specific_action = SPECIFIC_ACTIONS.get(issue, "Investigate root cause and apply fix")
    
    steps = [step.format(component=component, specific_action=specific_action) for step in template]
    return "\n".join(steps)

def generate_incidents(num_incidents=50):
    """Generate a specified number of IT incidents."""
    incidents = []
    
    for _ in range(num_incidents):
        component = random.choice(list(ISSUES.keys()))
        issue = random.choice(ISSUES[component])
        
        incident = {
            "description": generate_incident_description(component, issue),
            "resolution_process": generate_resolution_steps(component, issue),
            "kb_article_link": generate_kb_link(component, issue),
            "component": component,
            "issue_type": issue
        }
        incidents.append(incident)
    
    return incidents

def save_incidents_as_text(incidents, output_file="it_incidents.txt"):
    """Save incidents in a format suitable for the RAG system."""
    with open(f"{output_file}", "w") as f:
        for i, incident in enumerate(incidents, 1):
            f.write(f"Incident {i}\n")
            f.write("="* 80 + "\n\n")
            
            f.write("Description:\n")
            f.write("-"* 40 + "\n")
            f.write(incident["description"] + "\n\n")
            
            f.write("Resolution Process:\n")
            f.write("-"* 40 + "\n")
            f.write(incident["resolution_process"] + "\n\n")
            
            f.write("Knowledge Base Article:\n")
            f.write("-"* 40 + "\n")
            f.write(incident["kb_article_link"] + "\n\n\n")

if __name__ == "__main__":
    # Generate incidents
    incidents = generate_incidents(50)  # Generate 50 incidents
    
    # Save as text file
    save_incidents_as_text(incidents)
    
    # Also save as JSON for reference
    with open("it_incidents.json", "w") as f:
        json.dump(incidents, f, indent=2)
    
    print("Generated 50 IT incidents and saved to:")
    print("- code/data/it_incidents.txt (for RAG system)")
    print("- code/data/it_incidents.json (for reference)") 