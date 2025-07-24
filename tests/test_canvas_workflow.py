#!/usr/bin/env python3
"""
Test script for Canvas workflow execution
Tests the refined mapper with the actual Canvas JSON output
"""

import json
import logging
import requests
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def test_canvas_workflow_direct():
    """Test Canvas workflow execution directly (without API server)"""
    print("=== Testing Canvas Workflow Direct Execution ===")
    
    try:
        # Import modules
        from opentrons_functions import OpentronsController
        from workflow_mapper import WorkflowMapper
        
        # Load Canvas JSON
        with open('../data/test_workflow-1753364156528.json', 'r') as f:
            canvas_json = json.load(f)
        
        print(f"Loaded Canvas workflow: {canvas_json['metadata']['name']}")
        print(f"Node count: {len(canvas_json['workflow']['nodes'])}")
        
        # Initialize controller in dry-run mode
        controller = OpentronsController(dry_run=True)
        mapper = WorkflowMapper(controller)
        
        # Setup basic labware for testing
        print("Setting up labware...")
        controller.load_labware(1, "opentrons_96_tiprack_1000ul")
        controller.load_custom_labware(2, "./labware/nis_8_reservoir_25000ul.json")
        controller.load_custom_labware(9, "./labware/nis_15_wellplate_3895ul.json")
        controller.load_custom_labware(10, "./labware/nistall_4_tiprack_1ul.json")
        controller.load_pipette("p1000_single_gen2", "right")
        
        # Execute Canvas workflow
        print("Executing Canvas workflow...")
        result = mapper.execute_canvas_workflow(canvas_json)
        
        # Print results
        print(f"\n=== Execution Results ===")
        print(f"Status: {result['status']}")
        print(f"Total nodes: {result['total_nodes']}")
        print(f"Executed nodes: {result['executed_nodes']}")
        print(f"Successful nodes: {result['successful_nodes']}")
        print(f"Failed nodes: {len(result['failed_nodes'])}")
        
        if result['failed_nodes']:
            print(f"\nFailed Nodes:")
            for failed in result['failed_nodes']:
                print(f"  - {failed['node_type']} ({failed['node_id']}): {failed['error']}")
        
        print(f"\nSDL1 Operations Log:")
        for op in result['sdl1_operation_log']:
            print(f"  - {op['operation']}: {op['result']['status']}")
        
        return True
        
    except Exception as e:
        print(f"Direct test failed: {str(e)}")
        return False

def test_canvas_workflow_api():
    """Test Canvas workflow execution via API"""
    print("\n=== Testing Canvas Workflow API ===")
    
    try:
        # Load Canvas JSON
        with open('../data/test_workflow-1753364156528.json', 'r') as f:
            canvas_json = json.load(f)
        
        # Test validation endpoint first
        print("Testing validation endpoint...")
        response = requests.post(
            "http://localhost:8000/canvas/validate",
            json=canvas_json,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            validation_result = response.json()
            print(f"Validation: {validation_result['validation']['valid']}")
            if not validation_result['validation']['valid']:
                print(f"Validation errors: {validation_result['validation']['errors']}")
        else:
            print(f"Validation failed: {response.status_code} - {response.text}")
            return False
        
        # Test dry-run execution
        print("Testing dry-run execution...")
        response = requests.post(
            "http://localhost:8000/canvas/execute/dry-run",
            json=canvas_json,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            execution_result = response.json()
            print(f"Dry-run Status: {execution_result['execution']['status']}")
            print(f"Nodes executed: {execution_result['execution']['executed_nodes']}")
        else:
            print(f"Dry-run failed: {response.status_code} - {response.text}")
            return False
        
        print("API tests completed successfully!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("API server not running. Start with: python api_server.py")
        return False
    except Exception as e:
        print(f"API test failed: {str(e)}")
        return False

def generate_test_report():
    """Generate a test report"""
    print("\n=== Canvas Workflow Integration Test Report ===")
    print(f"Test Date: {datetime.now().isoformat()}")
    print(f"Canvas JSON File: ../data/test_workflow-1753364156528.json")
    
    # Test direct execution
    direct_success = test_canvas_workflow_direct()
    
    # Test API execution
    api_success = test_canvas_workflow_api()
    
    print(f"\n=== Test Summary ===")
    print(f"Direct Execution: {'✅ PASS' if direct_success else '❌ FAIL'}")
    print(f"API Execution: {'✅ PASS' if api_success else '❌ FAIL'}")
    
    if direct_success and api_success:
        print("🎉 All tests passed! Canvas integration is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")

if __name__ == "__main__":
    generate_test_report()