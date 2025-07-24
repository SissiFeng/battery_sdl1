# SDL1 Backend Testing Manual for Lab Personnel

## Overview

This manual provides step-by-step instructions for testing the refactored SDL1 backend system. The system now supports two workflow management options:

1. **Native Manager** - Simple, built-in workflow execution
2. **Prefect Manager** - Advanced workflow orchestration with monitoring and scheduling

## 🚀 Quick Start

### Prerequisites

1. **Python Environment**: Ensure Python 3.8+ is installed
2. **Dependencies**: Install required packages
3. **Hardware**: Opentrons robot (or simulation mode)
4. **Network**: Proper network connectivity to robot

### Installation

```bash
# Navigate to project directory
cd /path/to/battery_sdl1

# Install core dependencies
pip install -r requirements.txt

# Optional: Install Prefect for advanced features
pip install prefect>=2.10.0 prefect-shell>=0.1.0
```

## 🧪 Testing Workflow

### Step 1: Start the Backend Server

```bash
# Start the API server
python src/api_server.py

# Expected output:
# INFO:     Started server process
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

**✅ Success Indicator**: Server starts without errors and shows "Uvicorn running"

### Step 2: Verify Server Health

```bash
# Test basic connectivity
curl http://localhost:8000/

# Expected response:
# {"message": "SDL1 Workflow API is running", "version": "1.0.0"}
```

**✅ Success Indicator**: JSON response with API status

### Step 3: Check Available Workflow Managers

```bash
# Get available workflow managers
curl http://localhost:8000/managers

# Expected response:
# {
#   "managers": {
#     "native": {"available": true, ...},
#     "prefect": {"available": true/false, ...}
#   },
#   "current_manager": "native",
#   "prefect_available": true/false
# }
```

**✅ Success Indicator**: Response shows both managers with availability status

### Step 4: Configure Workflow Manager

#### Option A: Use Native Manager (Default)
```bash
curl -X POST "http://localhost:8000/managers/configure" \
  -H "Content-Type: application/json" \
  -d '{
    "manager_type": "native",
    "dry_run": true,
    "robot_ip": "169.254.69.185"
  }'

# Expected response:
# {
#   "status": "success",
#   "manager_type": "native",
#   "message": "Workflow manager configured: native"
# }
```

#### Option B: Use Prefect Manager (Advanced)
```bash
curl -X POST "http://localhost:8000/managers/configure" \
  -H "Content-Type: application/json" \
  -d '{
    "manager_type": "prefect",
    "dry_run": true,
    "robot_ip": "169.254.69.185"
  }'

# Expected response (if Prefect installed):
# {
#   "status": "success",
#   "manager_type": "prefect",
#   "message": "Workflow manager configured: prefect"
# }

# Expected response (if Prefect not installed):
# {
#   "error": "Prefect not available",
#   "message": "Install Prefect with: pip install prefect>=2.10.0"
# }
```

**✅ Success Indicator**: Configuration succeeds with chosen manager type

### Step 5: Test Canvas JSON Workflow Execution

#### Prepare Test Workflow
Use the provided test workflow file: `data/test_workflow-1753364156528.json`

```bash
# Verify test file exists
ls -la data/test_workflow-1753364156528.json

# View workflow structure
head -20 data/test_workflow-1753364156528.json
```

#### Execute Workflow (Dry Run)
```bash
curl -X POST "http://localhost:8000/canvas/execute/dry-run" \
  -H "Content-Type: application/json" \
  -d @data/test_workflow-1753364156528.json

# Expected response:
# {
#   "status": "success",
#   "workflow_name": "Test Workflow",
#   "executed_nodes": X,
#   "successful_nodes": X,
#   "failed_nodes": [],
#   "results": [...],
#   "execution_timestamp": "2024-XX-XXTXX:XX:XX"
# }
```

**✅ Success Indicator**: Workflow executes without errors, all nodes successful

#### Execute Workflow (Live Run)
⚠️ **Warning**: Only run this with proper robot setup and safety measures

```bash
curl -X POST "http://localhost:8000/canvas/execute" \
  -H "Content-Type: application/json" \
  -d @data/test_workflow-1753364156528.json
```

### Step 6: Test Individual Operations

#### Test Robot Status
```bash
curl http://localhost:8000/status

# Expected response:
# {
#   "robot": {
#     "status": "ready",
#     "connected": true
#   },
#   "timestamp": "2024-XX-XXTXX:XX:XX"
# }
```

#### Test Workflow Validation
```bash
curl -X POST "http://localhost:8000/canvas/validate" \
  -H "Content-Type: application/json" \
  -d @data/test_workflow-1753364156528.json

# Expected response:
# {
#   "valid": true,
#   "message": "Workflow validation successful",
#   "node_count": X,
#   "validation_details": {...}
# }
```

## 🔄 Switching Between Managers

### Scenario 1: Switch from Native to Prefect

```bash
# 1. Check current manager
curl http://localhost:8000/managers

# 2. Configure Prefect manager
curl -X POST "http://localhost:8000/managers/configure" \
  -H "Content-Type: application/json" \
  -d '{"manager_type": "prefect", "dry_run": true}'

# 3. Verify switch
curl http://localhost:8000/managers

# 4. Test workflow execution with Prefect
curl -X POST "http://localhost:8000/canvas/execute/dry-run" \
  -H "Content-Type: application/json" \
  -d @data/test_workflow-1753364156528.json
```

### Scenario 2: Switch from Prefect to Native

```bash
# 1. Configure native manager
curl -X POST "http://localhost:8000/managers/configure" \
  -H "Content-Type: application/json" \
  -d '{"manager_type": "native", "dry_run": true}'

# 2. Test workflow execution with native manager
curl -X POST "http://localhost:8000/canvas/execute/dry-run" \
  -H "Content-Type: application/json" \
  -d @data/test_workflow-1753364156528.json
```

## 🔍 Advanced Testing with Prefect

### Prerequisites for Prefect Testing
```bash
# Install Prefect
pip install prefect>=2.10.0 prefect-shell>=0.1.0

# Start Prefect server (in separate terminal)
python src/prefect_cli.py server
```

### Test Prefect Features

#### 1. Deploy a Workflow
```bash
python src/prefect_cli.py deploy \
  data/test_workflow-1753364156528.json \
  "Test SDL1 Workflow"
```

#### 2. List Deployments
```bash
python src/prefect_cli.py list-deployments
```

#### 3. Run Deployed Workflow
```bash
python src/prefect_cli.py run "Test SDL1 Workflow"
```

#### 4. Monitor via Web UI
Open browser to: http://127.0.0.1:4200

## 🐛 Troubleshooting Guide

### Common Issues and Solutions

#### Issue 1: Server Won't Start
**Symptoms**: ImportError, ModuleNotFoundError
**Solution**:
```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Install missing dependencies
pip install -r requirements.txt

# Verify imports
python -c "from src.api_server import app; print('OK')"
```

#### Issue 2: Robot Connection Failed
**Symptoms**: "Controller not initialized" error
**Solution**:
```bash
# Check robot IP
ping 169.254.69.185

# Use dry-run mode for testing
curl -X POST "http://localhost:8000/managers/configure" \
  -d '{"manager_type": "native", "dry_run": true}'
```

#### Issue 3: Prefect Not Available
**Symptoms**: "Prefect not available" error
**Solution**:
```bash
# Install Prefect
pip install prefect>=2.10.0 prefect-shell>=0.1.0

# Verify installation
python -c "import prefect; print(f'Prefect {prefect.__version__}')"
```

#### Issue 4: Workflow Execution Fails
**Symptoms**: Failed nodes in response
**Solution**:
1. Check workflow JSON format
2. Verify all required parameters
3. Use dry-run mode first
4. Check server logs for detailed errors

### Log Analysis

#### Server Logs
```bash
# Check recent logs
tail -f opentrons_api_$(date +%Y%m%d).log

# Search for errors
grep -i error opentrons_api_$(date +%Y%m%d).log
```

#### Debug Mode
```bash
# Start server with debug logging
PYTHONPATH=src python src/api_server.py --log-level debug
```

## 📊 Performance Testing

### Load Testing
```bash
# Test multiple concurrent requests
for i in {1..5}; do
  curl -X POST "http://localhost:8000/canvas/execute/dry-run" \
    -H "Content-Type: application/json" \
    -d @data/test_workflow-1753364156528.json &
done
wait
```

### Memory Usage
```bash
# Monitor server memory usage
ps aux | grep api_server
top -p $(pgrep -f api_server)
```

## ✅ Test Checklist

### Basic Functionality
- [ ] Server starts successfully
- [ ] Health check responds
- [ ] Manager configuration works
- [ ] Workflow validation passes
- [ ] Dry-run execution succeeds
- [ ] Manager switching works

### Native Manager
- [ ] Workflow execution completes
- [ ] All nodes execute successfully
- [ ] Results are properly formatted
- [ ] Error handling works

### Prefect Manager (if available)
- [ ] Prefect server starts
- [ ] Workflow deployment succeeds
- [ ] Scheduled execution works
- [ ] Web UI accessible
- [ ] Monitoring data available

### Integration Testing
- [ ] Canvas JSON format accepted
- [ ] All SDL1 operations supported
- [ ] Robot communication works
- [ ] Data export functions
- [ ] Error recovery mechanisms

## 📞 Support

### Getting Help
1. Check this manual first
2. Review server logs
3. Test with dry-run mode
4. Verify network connectivity
5. Check Python environment

### Reporting Issues
When reporting issues, include:
- Error messages from logs
- Steps to reproduce
- System configuration
- Workflow JSON (if relevant)
- Manager type being used

## 🧬 Canvas Integration Testing

### Testing Canvas JSON Format

#### Valid Canvas JSON Structure
```json
{
  "metadata": {
    "name": "Test Workflow",
    "id": "workflow-123",
    "version": "1.0",
    "created": "2024-07-24T10:00:00Z"
  },
  "workflow": {
    "nodes": [
      {
        "id": "node1",
        "type": "sdl1ExperimentSetup",
        "params": {
          "experiment_id": "exp-001",
          "temperature": 25,
          "pressure": 1.0
        }
      }
    ]
  }
}
```

#### Test Different Canvas Scenarios

**Scenario 1: Simple Linear Workflow**
```bash
# Create test workflow
cat > test_linear.json << 'EOF'
{
  "metadata": {"name": "Linear Test", "id": "linear-001"},
  "workflow": {
    "nodes": [
      {"id": "setup", "type": "sdl1ExperimentSetup", "params": {"experiment_id": "test"}},
      {"id": "prep", "type": "sdl1SolutionPreparation", "params": {"volume": 100}},
      {"id": "measure", "type": "sdl1ElectrochemicalMeasurement", "params": {"measurement_type": "CV"}}
    ]
  }
}
EOF

# Test execution
curl -X POST "http://localhost:8000/canvas/execute/dry-run" \
  -H "Content-Type: application/json" \
  -d @test_linear.json
```

**Scenario 2: Complex Multi-Step Workflow**
```bash
# Test with the provided complex workflow
curl -X POST "http://localhost:8000/canvas/execute/dry-run" \
  -H "Content-Type: application/json" \
  -d @data/test_workflow-1753364156528.json
```

**Scenario 3: Error Handling**
```bash
# Create invalid workflow
cat > test_invalid.json << 'EOF'
{
  "metadata": {"name": "Invalid Test"},
  "workflow": {
    "nodes": [
      {"id": "invalid", "type": "unknownOperation", "params": {}}
    ]
  }
}
EOF

# Test error handling
curl -X POST "http://localhost:8000/canvas/validate" \
  -H "Content-Type: application/json" \
  -d @test_invalid.json
```

## 🔬 SDL1 Operations Testing

### Test Each SDL1 Operation Type

#### 1. Experiment Setup
```bash
curl -X POST "http://localhost:8000/canvas/execute/dry-run" \
  -H "Content-Type: application/json" \
  -d '{
    "metadata": {"name": "Setup Test"},
    "workflow": {
      "nodes": [{
        "id": "setup1",
        "type": "sdl1ExperimentSetup",
        "params": {
          "experiment_id": "test-001",
          "temperature": 25,
          "pressure": 1.0,
          "humidity": 50
        }
      }]
    }
  }'
```

#### 2. Solution Preparation
```bash
curl -X POST "http://localhost:8000/canvas/execute/dry-run" \
  -H "Content-Type: application/json" \
  -d '{
    "metadata": {"name": "Solution Test"},
    "workflow": {
      "nodes": [{
        "id": "solution1",
        "type": "sdl1SolutionPreparation",
        "params": {
          "volume": 500,
          "concentration": 0.1,
          "solvent": "water",
          "mixing_time": 60
        }
      }]
    }
  }'
```

#### 3. Electrode Setup
```bash
curl -X POST "http://localhost:8000/canvas/execute/dry-run" \
  -H "Content-Type: application/json" \
  -d '{
    "metadata": {"name": "Electrode Test"},
    "workflow": {
      "nodes": [{
        "id": "electrode1",
        "type": "sdl1ElectrodeSetup",
        "params": {
          "electrode_type": "working",
          "material": "platinum",
          "surface_area": 1.0
        }
      }]
    }
  }'
```

#### 4. Electrochemical Measurement
```bash
curl -X POST "http://localhost:8000/canvas/execute/dry-run" \
  -H "Content-Type: application/json" \
  -d '{
    "metadata": {"name": "Measurement Test"},
    "workflow": {
      "nodes": [{
        "id": "measure1",
        "type": "sdl1ElectrochemicalMeasurement",
        "params": {
          "measurement_type": "CV",
          "scan_rate": 0.1,
          "potential_range": [-1.0, 1.0],
          "cycles": 3
        }
      }]
    }
  }'
```

## 🔄 Manager Comparison Testing

### Performance Comparison

#### Test Execution Time
```bash
# Time native manager execution
time curl -X POST "http://localhost:8000/managers/configure" \
  -d '{"manager_type": "native", "dry_run": true}'

time curl -X POST "http://localhost:8000/canvas/execute/dry-run" \
  -d @data/test_workflow-1753364156528.json

# Time Prefect manager execution (if available)
time curl -X POST "http://localhost:8000/managers/configure" \
  -d '{"manager_type": "prefect", "dry_run": true}'

time curl -X POST "http://localhost:8000/canvas/execute/dry-run" \
  -d @data/test_workflow-1753364156528.json
```

#### Feature Comparison Test
```bash
# Get manager capabilities
curl http://localhost:8000/managers | jq '.managers'

# Test manager switching speed
for manager in native prefect; do
  echo "Testing $manager manager..."
  time curl -X POST "http://localhost:8000/managers/configure" \
    -d "{\"manager_type\": \"$manager\", \"dry_run\": true}"
done
```

## 📈 Monitoring and Logging

### Log File Analysis

#### Check Different Log Levels
```bash
# Error logs
grep -i "error" opentrons_api_$(date +%Y%m%d).log

# Warning logs
grep -i "warning" opentrons_api_$(date +%Y%m%d).log

# Info logs
grep -i "info" opentrons_api_$(date +%Y%m%d).log

# Workflow execution logs
grep -i "workflow" opentrons_api_$(date +%Y%m%d).log
```

#### Real-time Monitoring
```bash
# Monitor logs in real-time
tail -f opentrons_api_$(date +%Y%m%d).log | grep -E "(ERROR|WARNING|workflow)"

# Monitor API requests
tail -f opentrons_api_$(date +%Y%m%d).log | grep -E "(POST|GET|PUT|DELETE)"
```

### System Resource Monitoring

#### Memory Usage
```bash
# Monitor memory usage during workflow execution
while true; do
  ps aux | grep -E "(api_server|python)" | grep -v grep
  sleep 5
done
```

#### Network Monitoring
```bash
# Monitor network connections
netstat -an | grep :8000

# Check robot connectivity
ping -c 5 169.254.69.185
```

## 🚨 Emergency Procedures

### Emergency Stop
```bash
# Stop workflow execution (if supported)
curl -X POST "http://localhost:8000/emergency-stop"

# Kill server process
pkill -f api_server

# Force kill if necessary
pkill -9 -f api_server
```

### Recovery Procedures

#### Server Recovery
```bash
# 1. Check for hanging processes
ps aux | grep -E "(api_server|python)"

# 2. Clean up processes
pkill -f api_server

# 3. Restart server
python src/api_server.py

# 4. Verify recovery
curl http://localhost:8000/
```

#### Robot Recovery
```bash
# 1. Check robot status
curl http://localhost:8000/status

# 2. Reset robot connection
curl -X POST "http://localhost:8000/managers/configure" \
  -d '{"manager_type": "native", "dry_run": true, "robot_ip": "169.254.69.185"}'

# 3. Test basic operations
curl -X POST "http://localhost:8000/canvas/validate" \
  -d @data/test_workflow-1753364156528.json
```

## 📋 Daily Testing Checklist

### Morning Startup
- [ ] Start backend server
- [ ] Verify robot connectivity
- [ ] Test basic API endpoints
- [ ] Configure preferred manager
- [ ] Run test workflow (dry-run)

### Before Experiments
- [ ] Validate workflow JSON
- [ ] Check robot status
- [ ] Verify manager configuration
- [ ] Test dry-run execution
- [ ] Review safety parameters

### After Experiments
- [ ] Check execution logs
- [ ] Verify data export
- [ ] Review error reports
- [ ] Backup workflow results
- [ ] Clean up temporary files

### End of Day
- [ ] Review daily logs
- [ ] Check system resources
- [ ] Backup important data
- [ ] Document any issues
- [ ] Plan next day's tests

## 🛡️ Recovery System Testing

### Overview

The SDL1 system now includes a comprehensive error recovery system with:
- **Checkpoint-based recovery**: Save system state at critical points
- **Hierarchical error handling**: Different strategies for different error types
- **Automatic retry mechanisms**: Intelligent retry with backoff
- **Recovery statistics**: Monitor system reliability

### Testing Recovery Features

#### Test Recovery Manager Initialization
```bash
# Test recovery system demo
python demo_recovery_system.py

# Expected output:
# ✅ Recovery manager initialized
# 📋 Started workflow: demo_workflow_001
# ✅ Operation result: success
# 📊 Checkpoints created: 1
```

#### Test Error Recovery Scenarios

**Scenario 1: Minor Error (Pipetting)**
```bash
curl -X POST "http://localhost:8000/canvas/execute/dry-run" \
  -H "Content-Type: application/json" \
  -d '{
    "metadata": {"name": "Recovery Test - Pipetting"},
    "workflow": {
      "nodes": [{
        "id": "test_pipetting",
        "type": "sdl1SolutionPreparation",
        "params": {
          "volume": 1000,
          "source_well": "A1",
          "target_well": "A1",
          "step_index": 1
        }
      }]
    }
  }'

# Check for recovery statistics in response
```

**Scenario 2: Moderate Error (Electrode Setup)**
```bash
curl -X POST "http://localhost:8000/canvas/execute/dry-run" \
  -H "Content-Type: application/json" \
  -d '{
    "metadata": {"name": "Recovery Test - Electrode"},
    "workflow": {
      "nodes": [{
        "id": "test_electrode",
        "type": "sdl1ElectrodeSetup",
        "params": {
          "electrode_type": "working",
          "position": "A1",
          "step_index": 2
        }
      }]
    }
  }'
```

#### Test Checkpoint Management

**Create and Verify Checkpoints**
```bash
# Execute workflow that creates checkpoints
curl -X POST "http://localhost:8000/canvas/execute/dry-run" \
  -d @data/test_workflow-1753364156528.json

# Check checkpoint directory
ls -la checkpoints/

# Expected files:
# demo_workflow_*_experiment_setup_complete_*.json
# demo_workflow_*_solution_preparation_complete_*.json
```

#### Test Recovery Statistics

**Get Recovery Performance Data**
```bash
# After running workflows, check logs for recovery stats
grep -i "recovery" opentrons_api_$(date +%Y%m%d).log

# Look for entries like:
# Recovery stats: 2 errors, 100.0% success rate
# Checkpoint saved: solution_preparation_complete at step 1
```

### Recovery Configuration

#### Configure Recovery Settings
```bash
# View recovery configuration
cat config/recovery_config.json

# Key settings to verify:
# - enable_recovery: true
# - max_retries for each operation type
# - checkpoint strategy
# - error severity mapping
```

#### Test Different Recovery Strategies

**Test Retry Strategy (Minor Errors)**
- Pipetting errors → Automatic retry up to 3 times
- Small delays between retries
- Success after retry should be logged

**Test Checkpoint Restart (Moderate Errors)**
- Electrode setup errors → Restart from last checkpoint
- System state restoration
- Continue from checkpoint position

**Test Safe Stop (Severe Errors)**
- Communication errors → Safe stop all operations
- Save emergency state
- Require manual intervention

### Recovery System Checklist

#### Basic Recovery Features
- [ ] Recovery manager initializes successfully
- [ ] Checkpoints are created at critical points
- [ ] Error classification works correctly
- [ ] Retry mechanisms function properly
- [ ] Recovery statistics are tracked

#### Error Handling
- [ ] Minor errors trigger retry strategy
- [ ] Moderate errors trigger checkpoint restart
- [ ] Severe errors trigger safe stop
- [ ] Critical errors trigger emergency stop
- [ ] Recovery attempts are logged

#### Checkpoint Management
- [ ] Checkpoints save system state correctly
- [ ] Checkpoint restoration works
- [ ] Old checkpoints are cleaned up
- [ ] Checkpoint files are properly formatted
- [ ] Emergency state saving functions

#### Integration Testing
- [ ] SDL1 operations use recovery system
- [ ] Workflow execution includes checkpoints
- [ ] API endpoints support recovery features
- [ ] Recovery works with both managers (Native/Prefect)
- [ ] Performance impact is acceptable

### Recovery Troubleshooting

#### Common Recovery Issues

**Issue 1: Recovery Manager Not Available**
**Symptoms**: "Recovery manager not available" warnings
**Solution**:
```bash
# Check recovery_manager.py import
python -c "from src.recovery_manager import RecoveryManager; print('OK')"

# Verify SDL1Operations initialization
python -c "from src.sdl1_operations import SDL1Operations; print('OK')"
```

**Issue 2: Checkpoints Not Created**
**Symptoms**: No checkpoint files in checkpoints/ directory
**Solution**:
```bash
# Check checkpoint directory permissions
ls -la checkpoints/
mkdir -p checkpoints
chmod 755 checkpoints

# Verify checkpoint creation in logs
grep -i checkpoint opentrons_api_$(date +%Y%m%d).log
```

**Issue 3: Recovery Not Triggered**
**Symptoms**: Errors don't trigger recovery mechanisms
**Solution**:
```bash
# Check recovery configuration
cat config/recovery_config.json | jq '.recovery_settings.enable_recovery'

# Verify error types are properly classified
grep -i "recoverable" opentrons_api_$(date +%Y%m%d).log
```

**Issue 4: Performance Impact**
**Symptoms**: Slow workflow execution with recovery enabled
**Solution**:
```bash
# Monitor checkpoint overhead
grep -i "checkpoint.*saved" opentrons_api_$(date +%Y%m%d).log

# Adjust checkpoint frequency in config
# Set "auto_checkpoint_frequency": "after_critical_operations"
```

### Recovery Performance Testing

#### Measure Recovery Overhead
```bash
# Test without recovery
time curl -X POST "http://localhost:8000/managers/configure" \
  -d '{"manager_type": "native", "dry_run": true}'

time curl -X POST "http://localhost:8000/canvas/execute/dry-run" \
  -d @data/test_workflow-1753364156528.json

# Test with recovery (compare execution times)
```

#### Test Recovery Success Rates
```bash
# Run multiple workflows and check statistics
for i in {1..5}; do
  curl -X POST "http://localhost:8000/canvas/execute/dry-run" \
    -d @data/test_workflow-1753364156528.json
done

# Check aggregated recovery statistics in logs
grep -i "success rate" opentrons_api_$(date +%Y%m%d).log
```

---

**Last Updated**: 2024-07-24
**Version**: 1.1
**Contact**: Development Team
