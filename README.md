# Battery SDL1 - Orchestrator based on Canvas

A comprehensive workflow mapping system for SDL1 (Self-Driving Laboratory 1) operations using Opentrons robots and electrochemical equipment.

## 🚀 Overview

This repository contains the backend system for executing automated battery research workflows using:
- **Opentrons OT-2 Robot**: Liquid handling and automation
- **Squidstat Potentiostat**: Electrochemical measurements
- **Arduino Controllers**: Cleaning and auxiliary operations
- **Canvas Workflow Engine**: Visual workflow design and execution

## 📁 Repository Structure

```
battery_sdl1/
├── src/                    # Source code
│   ├── api_server.py       # FastAPI server for workflow execution
│   ├── workflow_mapper.py  # JSON-to-function mapping system
│   ├── sdl1_operations.py  # SDL1-specific unit operations
│   └── opentrons_functions.py  # Opentrons robot control
├── tests/                  # Test suite
│   ├── test_*.py          # Various test modules
│   ├── final_integration_test.py  # Complete integration test
│   └── compatibility_report.json  # Test results
├── docs/                   # Documentation
├── demo/                  
├── data/                   # Sample data and workflows
│   ├── test_workflow-*.json  # Sample Canvas JSON workflows
│   └── ...
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🔧 Features

### SDL1 Operations Supported
- ✅ **Experiment Setup**: Hardware initialization and configuration
- ✅ **Solution Preparation**: Automated liquid handling and dispensing
- ✅ **Electrode Setup**: Electrode positioning and installation
- ✅ **Electrochemical Measurement**: OCV, CP, CVA, PEIS, LSV measurements
- ✅ **Wash/Cleaning**: Multi-stage cleaning with ultrasonic treatment
- ✅ **Data Export**: Automated data collection and export
- ✅ **Sequence Control**: Loop and conditional execution
- ✅ **Cycle Counter**: Progress monitoring and statistics

### Canvas JSON Format Support
- 📋 **Parameter Groups**: Organized parameter structure
- 🔄 **Execution Flow**: Advanced workflow control
- 📊 **Metadata**: Rich operation descriptions
- 🔄 **Backward Compatibility**: Supports legacy formats

## 🚀 Quick Start

### Prerequisites
```bash
# Python 3.8+
pip install -r requirements.txt

# Optional: Opentrons API (for real hardware)
pip install opentrons

# Optional: Squidstat libraries (for electrochemical measurements)
# Install from Admiral Instruments
```

### Running the API Server
```bash
cd src/
python api_server.py
```

### Testing the System
```bash
# Run all tests
cd tests/
python final_integration_test.py

# Test JSON compatibility
python test_json_compatibility.py

# Test specific components
python test_updated_mapper.py
```

### Example Usage
```python
from src.workflow_mapper import WorkflowMapper
from src.opentrons_functions import OpentronsController
import json

# Load Canvas workflow
with open('data/test_workflow-1753364156528.json', 'r') as f:
    workflow = json.load(f)

# Initialize system
controller = OpentronsController(dry_run=True)
mapper = WorkflowMapper(controller)

# Execute workflow
result = mapper.execute_canvas_workflow(workflow)
print(f"Status: {result['status']}")
```

## 📊 Test Results

- ✅ **JSON Compatibility**: 100% (all formats supported)
- ✅ **Operation Coverage**: 100% (8/8 SDL1 operations)
- ✅ **Parameter Handling**: 163 parameters processed correctly
- ✅ **Workflow Execution**: Complete success on test workflows
- ✅ **Backward Compatibility**: Legacy formats still supported

## 🔗 API Endpoints

- `POST /canvas/execute` - Execute Canvas workflow
- `POST /canvas/execute/dry-run` - Dry-run execution
- `POST /canvas/validate` - Validate workflow
- `GET /status` - System status
- `GET /operations` - Supported operations

## 📚 Documentation

Detailed documentation is available in the `docs/` directory:
- **Implementation Guide**: Complete implementation details
- **API Reference**: Endpoint documentation
- **Operation Manual**: SDL1 operation descriptions
- **Testing Guide**: Test suite documentation

## 🧪 Testing

The test suite includes:
- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end workflow testing
- **Compatibility Tests**: JSON format validation
- **API Tests**: Endpoint functionality testing

Run tests with:
```bash
cd tests/
python -m pytest  # If pytest is installed
# OR
python final_integration_test.py  # Standalone test
```


---

**Status**: ✅ Production Ready | **Version**: 2.0 | **Last Updated**: 2025-07-24
