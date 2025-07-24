# Prefect Workflow Management Guide

## Overview

The Battery SDL1 system now supports two workflow management options:

1. **Native Manager**: Built-in workflow execution with basic task management
2. **Prefect Manager**: Advanced workflow orchestration with monitoring, scheduling, and deployment capabilities

This guide explains how to use the Prefect-based workflow management system.

## 🚀 Quick Start

### Installation

```bash
# Install Prefect dependencies
pip install prefect>=2.10.0 prefect-shell>=0.1.0

# Verify installation
python -c "import prefect; print(f'Prefect {prefect.__version__} installed')"
```

### Basic Usage

```python
from src.workflow_manager_factory import UnifiedWorkflowInterface, WorkflowManagerType
import json

# Load workflow
with open('data/test_workflow-1753364156528.json', 'r') as f:
    workflow = json.load(f)

# Use Prefect manager
interface = UnifiedWorkflowInterface(manager_type=WorkflowManagerType.PREFECT)
result = interface.execute_workflow(workflow)

print(f"Status: {result['status']}")
print(f"Successful nodes: {result['successful_nodes']}")
```

## 🔧 Configuration

### Manager Selection

You can choose between workflow managers using the factory:

```python
from src.workflow_manager_factory import WorkflowManagerFactory, WorkflowManagerType
from src.opentrons_functions import OpentronsController

controller = OpentronsController(dry_run=True)

# Native manager (default)
native_manager = WorkflowManagerFactory.create_manager(
    WorkflowManagerType.NATIVE, controller
)

# Prefect manager
prefect_manager = WorkflowManagerFactory.create_manager(
    WorkflowManagerType.PREFECT, controller
)
```

### API Configuration

Configure the workflow manager via API:

```bash
# Configure to use Prefect
curl -X POST "http://localhost:8000/managers/configure" \
  -H "Content-Type: application/json" \
  -d '{
    "manager_type": "prefect",
    "dry_run": true,
    "robot_ip": "169.254.69.185"
  }'

# Check available managers
curl "http://localhost:8000/managers"
```

## 📊 Prefect Features

### Task Orchestration

Prefect provides advanced task management:

- **Automatic Retries**: Failed tasks are automatically retried with configurable delays
- **Error Handling**: Sophisticated error handling and recovery
- **Task Dependencies**: Automatic dependency resolution
- **Parallel Execution**: Support for parallel task execution (future feature)

### Monitoring and Logging

- **Real-time Monitoring**: Track workflow execution in real-time
- **Detailed Logging**: Comprehensive logging with structured data
- **Performance Metrics**: Task duration and success rates
- **Web UI**: Visual monitoring dashboard

### Scheduling and Deployment

- **Workflow Scheduling**: Schedule workflows to run at specific times or intervals
- **Deployment Management**: Deploy workflows as long-running services
- **Version Control**: Track workflow versions and changes

## 🖥️ Command Line Interface

### Prefect CLI

The system includes a CLI for Prefect management:

```bash
# Start Prefect server
python src/prefect_cli.py server

# Deploy a workflow
python src/prefect_cli.py deploy data/test_workflow-1753364156528.json "My SDL1 Workflow"

# Schedule with interval (every hour)
python src/prefect_cli.py deploy data/test_workflow-1753364156528.json "Hourly Workflow" --schedule "interval:3600"

# Schedule with cron (daily at 9 AM)
python src/prefect_cli.py deploy data/test_workflow-1753364156528.json "Daily Workflow" --schedule "cron:0 9 * * *"

# List deployments
python src/prefect_cli.py list-deployments

# Run a workflow
python src/prefect_cli.py run "My SDL1 Workflow"

# Check status
python src/prefect_cli.py status <flow-run-id>

# List recent runs
python src/prefect_cli.py list-runs

# Compare managers
python src/prefect_cli.py compare
```

## 🔄 Workflow Deployment

### Creating Deployments

```python
from src.prefect_deployment_manager import PrefectDeploymentManager
from src.opentrons_functions import OpentronsController
import json

# Initialize
controller = OpentronsController(dry_run=True)
deployment_manager = PrefectDeploymentManager(controller)

# Load workflow
with open('data/test_workflow-1753364156528.json', 'r') as f:
    workflow_json = json.load(f)

# Create deployment
deployment_id = await deployment_manager.create_workflow_deployment(
    workflow_name="SDL1 Battery Research",
    workflow_json=workflow_json,
    schedule={
        "type": "interval",
        "interval_seconds": 3600  # Every hour
    }
)
```

### Scheduling Workflows

```python
from datetime import datetime, timedelta

# Schedule for specific time
scheduled_time = datetime.now() + timedelta(hours=1)
flow_run_id = await deployment_manager.schedule_workflow_execution(
    deployment_name="SDL1 Battery Research",
    scheduled_time=scheduled_time,
    parameters={"dry_run": True}
)

# Check status
status = await deployment_manager.get_workflow_status(flow_run_id)
print(f"Workflow state: {status['state']}")
```

## 📈 Monitoring and Management

### Web UI

Start the Prefect server to access the web UI:

```bash
# Start server
python src/prefect_cli.py server

# Access UI at http://127.0.0.1:4200
```

The web UI provides:
- Real-time workflow monitoring
- Task execution details
- Performance metrics
- Deployment management
- Flow run history

### Programmatic Monitoring

```python
# Get recent workflow runs
recent_runs = await deployment_manager.get_recent_flow_runs(limit=10)

for run in recent_runs:
    print(f"Run: {run['name']} - State: {run['state']}")

# List all deployments
deployments = await deployment_manager.list_deployments()

for deployment in deployments:
    print(f"Deployment: {deployment['name']} - Active: {deployment['is_schedule_active']}")
```

## 🔍 Comparison: Native vs Prefect

### When to Use Native Manager

- **Simple workflows**: Basic sequential execution
- **Development/Testing**: Quick iteration and debugging
- **Minimal dependencies**: No additional software required
- **Research environments**: Flexible experimentation

### When to Use Prefect Manager

- **Production environments**: Robust error handling and monitoring
- **Scheduled workflows**: Automated execution at specific times
- **Complex workflows**: Advanced orchestration needs
- **Team collaboration**: Shared monitoring and management
- **Long-running processes**: Reliable execution over time

### Feature Comparison

| Feature | Native Manager | Prefect Manager |
|---------|----------------|-----------------|
| Task Execution | ✅ Sequential | ✅ Sequential + Parallel |
| Error Handling | ✅ Basic | ✅ Advanced + Retries |
| Monitoring | ✅ Logs only | ✅ Web UI + Metrics |
| Scheduling | ❌ None | ✅ Cron + Interval |
| Deployment | ❌ None | ✅ Full lifecycle |
| Dependencies | ✅ None | ⚠️ Prefect required |
| Learning Curve | ✅ Simple | ⚠️ Moderate |

## 🛠️ Troubleshooting

### Common Issues

1. **Prefect Not Available**
   ```bash
   pip install prefect>=2.10.0 prefect-shell>=0.1.0
   ```

2. **Server Connection Issues**
   ```bash
   # Start local Prefect server
   python src/prefect_cli.py server
   ```

3. **Import Errors**
   ```python
   # Check Prefect installation
   import prefect
   print(f"Prefect version: {prefect.__version__}")
   ```

### Getting Help

- Check the Prefect documentation: https://docs.prefect.io/
- Run the test suite: `python tests/test_prefect_workflow.py`
- Use the CLI comparison: `python src/prefect_cli.py compare`

## 📚 Examples

### Example 1: Basic Workflow Execution

```python
from src.workflow_manager_factory import UnifiedWorkflowInterface
import json

# Load and execute workflow
with open('data/test_workflow-1753364156528.json', 'r') as f:
    workflow = json.load(f)

interface = UnifiedWorkflowInterface(manager_type="prefect")
result = interface.execute_workflow(workflow)

print(f"Execution completed: {result['status']}")
```

### Example 2: Scheduled Deployment

```bash
# Deploy with daily schedule
python src/prefect_cli.py deploy \
  data/test_workflow-1753364156528.json \
  "Daily Battery Test" \
  --schedule "cron:0 9 * * *"
```

### Example 3: API Integration

```python
import requests

# Configure Prefect manager
response = requests.post("http://localhost:8000/managers/configure", json={
    "manager_type": "prefect",
    "dry_run": False
})

# Execute workflow
with open('data/test_workflow-1753364156528.json', 'r') as f:
    workflow = json.load(f)

response = requests.post("http://localhost:8000/canvas/execute", json=workflow)
result = response.json()
```

## 🎯 Best Practices

1. **Start with Native**: Begin with the native manager for development
2. **Use Prefect for Production**: Deploy with Prefect for production environments
3. **Monitor Regularly**: Use the web UI to monitor workflow health
4. **Handle Errors Gracefully**: Configure appropriate retry policies
5. **Version Control**: Track workflow changes and deployments
6. **Test Thoroughly**: Use dry-run mode for testing

---

**Next Steps**: Try the examples above and explore the Prefect web UI for advanced workflow management capabilities.
