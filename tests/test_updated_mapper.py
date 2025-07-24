#!/usr/bin/env python3
"""
Test script for the updated mapper with new JSON format
Tests all SDL1 operations with the new Canvas JSON structure
"""

import json
import logging
import sys
import os
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

class MockOpentronsController:
    """Mock controller for testing without Opentrons dependency"""
    
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.labware = {}
        self.pipettes = {}
        
    def delay(self, seconds, message=""):
        logging.info(f"DELAY: {seconds}s - {message}")
        
    def load_labware(self, slot, labware_type):
        self.labware[slot] = labware_type
        logging.info(f"LOAD_LABWARE: Slot {slot} - {labware_type}")
        
    def load_custom_labware(self, slot, labware_file):
        self.labware[slot] = labware_file
        logging.info(f"LOAD_CUSTOM_LABWARE: Slot {slot} - {labware_file}")
        
    def load_pipette(self, pipette_type, mount):
        self.pipettes[mount] = pipette_type
        logging.info(f"LOAD_PIPETTE: {pipette_type} on {mount}")
        
    def fill_well(self, **kwargs):
        logging.info(f"FILL_WELL: {kwargs}")
        return {"status": "success", "message": "Well filled"}
        
    def move_to_well(self, **kwargs):
        logging.info(f"MOVE_TO_WELL: {kwargs}")
        return {"status": "success", "message": "Moved to well"}

def test_mapper_with_new_json():
    """Test the updated mapper with the new JSON format"""
    print("=== Testing Updated Mapper with New JSON Format ===")
    
    try:
        # Import the updated modules
        sys.path.append('.')
        from sdl1_operations import SDL1Operations
        from workflow_mapper import WorkflowMapper
        
        # Load the new Canvas JSON
        with open('test_workflow-1753364156528.json', 'r') as f:
            canvas_json = json.load(f)
        
        print(f"✅ Loaded Canvas workflow: {canvas_json['metadata']['name']}")
        print(f"Node count: {len(canvas_json['workflow']['nodes'])}")
        
        # Initialize with mock controller
        mock_controller = MockOpentronsController(dry_run=True)
        sdl1_ops = SDL1Operations(mock_controller)
        mapper = WorkflowMapper(mock_controller)
        
        # Test each node type individually
        nodes = canvas_json['workflow']['nodes']
        
        for i, node in enumerate(nodes):
            node_type = node.get('type')
            node_id = node.get('id')
            node_params = node.get('params', {})
            
            print(f"\n--- Testing Node {i+1}: {node_type} ---")
            print(f"ID: {node_id}")
            print(f"Params count: {len(node_params)}")
            
            # Check if the operation is available in the mapper
            if node_type in mapper.function_map:
                print(f"✅ Operation {node_type} found in mapper")
                
                # Test parameter extraction
                required_params = ["uo_name", "description", "error_handling", "log_level"]
                missing_params = [p for p in required_params if p not in node_params]
                
                if missing_params:
                    print(f"⚠️  Missing required params: {missing_params}")
                else:
                    print(f"✅ All required params present")
                
                # Test execution (dry run)
                try:
                    result = mapper.execute_node(node)
                    print(f"✅ Execution result: {result.get('status', 'unknown')}")
                    if result.get('status') == 'error':
                        print(f"   Error: {result.get('message', 'Unknown error')}")
                except Exception as e:
                    print(f"❌ Execution failed: {str(e)}")
                    
            else:
                print(f"❌ Operation {node_type} NOT found in mapper")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_specific_operations():
    """Test specific operations with sample parameters"""
    print("\n=== Testing Specific Operations ===")
    
    try:
        sys.path.append('.')
        from sdl1_operations import SDL1Operations
        
        # Initialize with mock controller
        mock_controller = MockOpentronsController(dry_run=True)
        sdl1_ops = SDL1Operations(mock_controller)
        
        # Test sdl1ExperimentSetup
        print("\n--- Testing sdl1ExperimentSetup ---")
        setup_params = {
            "uo_name": "Test_Setup",
            "description": "Test experiment setup",
            "error_handling": "stop",
            "log_level": "INFO",
            "experiment_id": "Test_Experiment",
            "test_well_address": "A1",
            "robot_ip": "169.254.69.185",
            "robot_port": 80,
            "squidstat_port": "COM4",
            "squidstat_channel": 0,
            "validate_hardware_connection": False,
            "check_pipette_tips": False,
            "verify_well_availability": True
        }
        
        result = sdl1_ops.sdl1ExperimentSetup(setup_params)
        print(f"Result: {result.get('status')} - {result.get('message')}")
        
        # Test sdl1CycleCounter
        print("\n--- Testing sdl1CycleCounter ---")
        counter_params = {
            "uo_name": "Test_Counter",
            "description": "Test cycle counter",
            "error_handling": "stop",
            "log_level": "INFO",
            "current_cycle": 1,
            "total_cycles": 5,
            "cycle_type": "electrochemical",
            "display_enabled": True,
            "show_progress": True,
            "show_statistics": True
        }
        
        result = sdl1_ops.sdl1CycleCounter(counter_params)
        print(f"Result: {result.get('status')} - {result.get('message')}")
        
        # Test sdl1ElectrochemicalMeasurement with new format
        print("\n--- Testing sdl1ElectrochemicalMeasurement (New Format) ---")
        measurement_params = {
            "uo_name": "Test_Measurement",
            "description": "Test electrochemical measurement",
            "error_handling": "stop",
            "log_level": "INFO",
            "com_port": "COM4",
            "channel": 0,
            "measurement_type": "CP",
            "cp_current": -0.004,
            "cp_duration": 720,
            "cp_sample_interval": 1,
            "data_collection_enabled": True
        }
        
        result = sdl1_ops.sdl1ElectrochemicalMeasurement(measurement_params)
        print(f"Result: {result.get('status')} - {result.get('message')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Specific operations test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_workflow_execution():
    """Test full workflow execution"""
    print("\n=== Testing Full Workflow Execution ===")
    
    try:
        sys.path.append('.')
        from workflow_mapper import WorkflowMapper
        
        # Load the new Canvas JSON
        with open('test_workflow-1753364156528.json', 'r') as f:
            canvas_json = json.load(f)
        
        # Initialize with mock controller
        mock_controller = MockOpentronsController(dry_run=True)
        mapper = WorkflowMapper(mock_controller)
        
        # Execute the full Canvas workflow
        print("Executing full Canvas workflow...")
        result = mapper.execute_canvas_workflow(canvas_json)
        
        print(f"✅ Workflow execution completed")
        print(f"Status: {result.get('status')}")
        print(f"Executed nodes: {result.get('executed_nodes', 0)}")
        print(f"Successful nodes: {result.get('successful_nodes', 0)}")
        print(f"Failed nodes: {len(result.get('failed_nodes', []))}")
        
        if result.get('failed_nodes'):
            print("Failed nodes:")
            for failed in result.get('failed_nodes', []):
                print(f"  - {failed}")
        
        return result.get('status') == 'success'
        
    except Exception as e:
        print(f"❌ Workflow execution test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Updated Mapper with New Canvas JSON Format")
    print("=" * 60)
    
    # Test mapper compatibility
    mapper_ok = test_mapper_with_new_json()
    
    # Test specific operations
    operations_ok = test_specific_operations()
    
    # Test workflow execution
    workflow_ok = test_workflow_execution()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"Mapper Compatibility: {'✅ PASS' if mapper_ok else '❌ FAIL'}")
    print(f"Specific Operations: {'✅ PASS' if operations_ok else '❌ FAIL'}")
    print(f"Workflow Execution: {'✅ PASS' if workflow_ok else '❌ FAIL'}")
    
    if mapper_ok and operations_ok and workflow_ok:
        print("\n🎉 All tests passed! The updated mapper works with the new JSON format.")
    else:
        print("\n⚠️  Some tests failed. Check the logs above for details.")
    
    return mapper_ok and operations_ok and workflow_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
