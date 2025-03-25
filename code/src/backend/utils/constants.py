ARTIFACTS_DIR = "backend/vstore_artifacts"
DATA_DIR = "backend/incident_data"

RAGCHAIN_SYSTEMPROMPT ="""You are an AI assistant for IT incident management and resolution. You have access to a knowledge base of past incidents across various categories including Technology Security, Technology Processing, Data Integrity, Technology Performance, Technology Faults, Vendor/Third-Party issues, SACM Data Quality, and Sensitive Incidents.

Adapt your response based on the type of query:

1. If the user wants COMMANDS to resolve an issue:
   Provide relevant commands from KB articles directly, with brief explanations of what each does.
   IMPORTANT: Remember to add command: before the code block for all commands.
   Format: 
   command: 
   ```bash
   # Command purpose
   actual_command_here
   ```

2. If the user is TROUBLESHOOTING an active issue:
   Provide a concise troubleshooting plan with immediate actions first, followed by diagnostic commands.
   Include relevant KB articles and commands.
   Remember to add command: before the code block for all commands.
   
3. If the user wants a DETAILED ANALYSIS of an incident:
   Provide a comprehensive response with full categorization and similar incidents.

4. For GENERAL QUESTIONS about IT systems:
   Provide clear, concise information focused on IT best practices.
   
Default output for incident analysis (use when appropriate):

# Incident Analysis
🚨 **Category**: [Matching incident category]

📋 **Subcategory**: [Relevant subcategory]

⚠️ **Severity**: [High/Medium/Low]

👥 **Assignment Group**: [Relevant team]

🔧 **Affected System**: [System or service]

## Similar Incidents
[List relevant past incidents]

## Resolution Steps
[Prioritized steps with commands when appropriate. Remember to prefix all commands with "command:"]

## Knowledge Base References
[Relevant KB articles]

Guidelines:
1. Only respond to IT-related queries. For non-IT topics, politely explain you're an IT incident management assistant.
2. Adapt your response format to the query - be concise for direct questions, detailed for incident analysis.
3. For urgent issues, prioritize immediate mitigating commands before deeper analysis.
4. When providing commands, ALWAYS prefix them with "command:" to indicate they are executable.
5. If similar incidents exist in multiple categories, mention this for broader context.
6. When troubleshooting, provide steps in order of: containment, diagnosis, resolution, verification.
7. Remember: Every command in your response must be prefixed with "command:" to be recognized as executable.
""" 


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

RAG_LLM_PROMPT = """{system_prompt}

    Context:{context}

    Question/Incident: {query}

    Please provide a clear, step-by-step response. If there are multiple similar but distinct issues:
    1. Keep them separate and clearly labeled
    2. Highlight the key differences between them
    3. Present each with its own resolution steps
    4. Use "---" to separate different issues
    """ 

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


MOCK_KB_ARTICLES =  [
            {
                "id": "KB0020234",
                "title": "Database Connection Pool Management",
                "component": "database",
                "issue_type": "Connection Pool Exhaustion",
                "content": """
# Database Connection Pool Management

## Overview
This article explains how to manage database connection pools to prevent exhaustion issues.

## Symptoms
- Slow query response times
- Failed connections
- Application timeouts when accessing the database
- High wait times in connection acquisition

## Resolution Steps

### 1. Check Current Connection Usage
```bash
# For PostgreSQL
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"

# For MySQL
mysql -u root -p -e "SHOW PROCESSLIST;"
```

### 2. Identify Connection Leaks
```bash
# For PostgreSQL - Find idle connections
sudo -u postgres psql -c "SELECT pid, datname, usename, state, backend_start, query_start FROM pg_stat_activity WHERE state = 'idle';"
```

### 3. Adjust Pool Size
For PostgreSQL, edit postgresql.conf:
```
max_connections = 200       # Increase as needed
```

For connection poolers like PgBouncer:
```
pool_size = 20              # Connections per user/database pair
max_client_conn = 100       # Maximum number of client connections
```

### 4. Configure Connection Timeouts
```
idle_in_transaction_session_timeout = 300000  # 5 minutes in ms
```

### 5. Implement Application-Side Pooling
In application code, ensure proper connection handling:
- Always close connections in finally blocks
- Use connection pooling libraries
- Set appropriate timeout values

## Prevention
- Monitor connection pool metrics
- Implement alerts for high usage (>80%)
- Use connection pooling middleware
- Audit application code for connection leaks
                """
            },
            {
                "id": "KB0040234",
                "title": "API Gateway High CPU Troubleshooting",
                "component": "api-gateway",
                "issue_type": "High CPU Usage",
                "content": """
# API Gateway High CPU Troubleshooting

## Overview
This article covers troubleshooting and resolving high CPU usage on API Gateway instances.

## Symptoms
- CPU usage consistently above 80%
- Increased response latency
- Timeouts on API calls
- 503 Service Unavailable errors

## Resolution Steps

### 1. Check Gateway Health and Metrics
```bash
# Get current CPU and memory usage
top -bn1 | grep "Cpu(s)"
free -m

# Check process resource consumption
ps aux --sort=-%cpu | head -10
```

### 2. Analyze Traffic Patterns
```bash
# Check active connections
netstat -anp | grep :443 | wc -l

# Check access logs for traffic spikes
tail -n 1000 /var/log/nginx/access.log | cut -d ' ' -f 1 | sort | uniq -c | sort -nr | head -n 10
```

### 3. Optimize API Gateway Configuration
```bash
# Edit configuration file
nano /etc/nginx/nginx.conf

# Optimize worker settings
worker_processes auto;
worker_rlimit_nofile 65535;

# Optimize event settings
events {
    worker_connections 4096;
    multi_accept on;
    use epoll;
}
```

### 4. Implement Request Rate Limiting
```bash
# Add rate limiting configuration
http {
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    
    server {
        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;
        }
    }
}
```

### 5. Scale Gateway Resources
For cloud deployments:
- Increase instance size/type
- Add additional instances behind load balancer

For Kubernetes:
```bash
kubectl scale deployment api-gateway --replicas=5
```

## Prevention
- Implement auto-scaling based on CPU metrics
- Set up monitoring and alerting at 70% CPU threshold
- Regularly review and optimize API endpoints
- Implement proper caching strategies
                """
            },
            {
                "id": "KB0060234",
                "title": "Message Queue Backlog Management",
                "component": "message-queue",
                "issue_type": "Queue Backup",
                "content": """
# Message Queue Backlog Management

## Overview
This article covers how to resolve message queue backlogs and prevent future occurrences.

## Symptoms
- Rapidly growing queue depth
- Increased message processing latency
- Consumer lag metrics rising
- Slow or failed message publishing

## Resolution Steps

### 1. Assess Current Queue Status
```bash
# For RabbitMQ
rabbitmqctl list_queues name messages_ready messages_unacknowledged

# For Kafka
kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group consumer-group-name
```

### 2. Identify Bottlenecks
```bash
# Check consumer logs for errors
tail -n 1000 /var/log/consumer-service.log | grep ERROR

# Check for slow message processing
grep "processing time" /var/log/consumer-service.log | awk '{sum+=$NF; count++} END {print sum/count}'
```

### 3. Scale Up Consumers
```bash
# For Kubernetes-based deployments
kubectl scale deployment message-consumer --replicas=5

# For Docker Compose
docker-compose scale consumer=5
```

### 4. Optimize Consumer Configuration
```
# Increase prefetch count for batch processing
channel.basicQos(250, true);  # In code

# For Kafka consumers, increase partition count
kafka-topics.sh --bootstrap-server localhost:9092 --alter --topic my-topic --partitions 10
```

### 5. Implement Message Prioritization
For critical messages:
```
# Create a priority queue in RabbitMQ
rabbitmqctl set_policy priority-messages "^priority-.*" '{"max-priority":10}' --apply-to queues
```

### 6. Consider Message TTL for Non-Critical Messages
```
# Set TTL for low-priority messages
rabbitmqctl set_policy ttl-policy "^low-priority-.*" '{"message-ttl":3600000}' --apply-to queues
```

## Prevention
- Monitor queue depth with alerting thresholds
- Implement circuit breakers for producers during high load
- Design consumers to scale horizontally
- Implement dead letter queues for failed processing
                """
            }
    ]

MONITORING_SERVICES_MOCK_STATE =  {
            "api-gateway": {
                "cpu_usage": 87,  # High CPU scenario
                "memory_usage": 65,
                "request_rate": 420,
                "error_rate": 8.2,
                "status": "degraded",
                "response_time_ms": 350,
                "requests_per_second": 120
            },
            "database": {
                "connection_pool": {
                    "used": 180,
                    "max": 200,
                    "wait_time_ms": 250
                },
                "replication_lag_sec": 12,
                "cpu_usage": 72,
                "memory_usage": 85,
                "query_execution_time_ms": 420,
                "status": "warning",
                "active_queries": 35
            },
            "message-queue": {
                "queue_depth": 10500,
                "consumer_lag": 3200,
                "cpu_usage": 45,
                "memory_usage": 60,
                "publish_rate": 150,
                "consume_rate": 90,
                "status": "warning"
            },
            "auth-service": {
                "cpu_usage": 30,
                "memory_usage": 40,
                "request_rate": 85,
                "error_rate": 0.5,
                "response_time_ms": 120,
                "token_validation_rate": 110,
                "status": "healthy"
            }
}


MOCK_SERVICES = {
            "api-gateway": {
                "status": "running",
                "version": "1.5.2",
                "instances": 3,
                "config": {
                    "thread_pool_size": 25,
                    "max_connections": 500,
                    "timeout_ms": 3000,
                    "rate_limit": 1000
                }
            },
            "database": {
                "status": "running",
                "version": "PostgreSQL 14.2",
                "instances": 1,
                "config": {
                    "max_connections": 200,
                    "shared_buffers": "2GB",
                    "work_mem": "128MB",
                    "maintenance_work_mem": "256MB"
                }
            },
            "message-queue": {
                "status": "running",
                "version": "RabbitMQ 3.9.13",
                "instances": 2,
                "config": {
                    "queue_mode": "lazy",
                    "prefetch_count": 50,
                    "max_length": 100000,
                    "memory_threshold": "1GB"
                }
            },
            "auth-service": {
                "status": "running",
                "version": "2.1.0",
                "instances": 2,
                "config": {
                    "token_expiry": 3600,
                    "refresh_expiry": 86400,
                    "max_login_attempts": 5,
                    "rate_limit": 500
                }
            }
        }