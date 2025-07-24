#!/usr/bin/env python3
"""
Test script for JSON format compatibility
Tests parameter extraction and mapping without Opentrons dependencies
"""

import json
import logging
import sys
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def test_json_structure():
    """Test the JSON structure and parameter extraction"""
    print("=== Testing JSON Structure and Parameter Extraction ===")
    
    try:
        # Load the new Canvas JSON
        with open('../data/test_workflow-1753364156528.json', 'r') as f:
            canvas_json = json.load(f)
        
        print(f"✅ Loaded Canvas workflow: {canvas_json['metadata']['name']}")
        
        # Extract workflow structure
        workflow_data = canvas_json.get("workflow", {})
        nodes = workflow_data.get("nodes", [])
        metadata = canvas_json.get("metadata", {})
        
        print(f"Metadata: {list(metadata.keys())}")
        print(f"Workflow keys: {list(workflow_data.keys())}")
        print(f"Node count: {len(nodes)}")
        
        # Test each node
        operation_types = set()
        all_params = set()
        
        for i, node in enumerate(nodes):
            node_type = node.get('type')
            node_params = node.get('params', {})
            node_id = node.get('id')
            
            operation_types.add(node_type)
            all_params.update(node_params.keys())
            
            print(f"\nNode {i+1}: {node_type}")
            print(f"  ID: {node_id}")
            print(f"  Params: {len(node_params)}")
            
            # Check required common parameters
            required_params = ["uo_name", "description", "error_handling", "log_level"]
            missing_params = [p for p in required_params if p not in node_params]
            
            if missing_params:
                print(f"  ⚠️  Missing required params: {missing_params}")
            else:
                print(f"  ✅ All required params present")
            
            # Check for new metadata structure
            if 'metadata' in node and 'parameterGroups' in node['metadata']:
                param_groups = node['metadata']['parameterGroups']
                print(f"  📋 Parameter groups: {list(param_groups.keys())}")
            
            # Check for execution flow
            if 'executionFlow' in node:
                exec_flow = node['executionFlow']
                print(f"  🔄 Execution flow: {exec_flow.get('executionOrder', 'unknown')}")
        
        print(f"\n📊 Summary:")
        print(f"Operation types found: {sorted(operation_types)}")
        print(f"Total unique parameters: {len(all_params)}")
        
        return True
        
    except Exception as e:
        print(f"❌ JSON structure test failed: {str(e)}")
        return False

def test_parameter_mapping():
    """Test parameter mapping for each operation type"""
    print("\n=== Testing Parameter Mapping ===")
    
    try:
        # Load the new Canvas JSON
        with open('../data/test_workflow-1753364156528.json', 'r') as f:
            canvas_json = json.load(f)
        
        nodes = canvas_json['workflow']['nodes']
        
        # Define expected parameters for each operation type
        expected_params = {
            "sdl1ExperimentSetup": [
                "experiment_id", "test_well_address", "robot_ip", "robot_port",
                "squidstat_port", "squidstat_channel", "validate_hardware_connection"
            ],
            "sdl1SolutionPreparation": [
                "source_labware", "source_well", "target_labware", "target_well",
                "volume", "pipette_type"
            ],
            "sdl1ElectrodeSetup": [
                "electrode_type", "electrode_position", "target_well", "insertion_depth"
            ],
            "sdl1ElectrochemicalMeasurement": [
                "com_port", "channel", "measurement_type", "cp_current", "cp_duration"
            ],
            "sdl1WashCleaning": [
                "cleaning_cycles", "ultrasonic_time", "pump1_volume", "pump2_volume"
            ],
            "sdl1DataExport": [
                "export_format", "file_path", "include_metadata", "data_tag"
            ],
            "sdl1SequenceControl": [
                "loop_count", "loop_condition", "break_condition"
            ],
            "sdl1CycleCounter": [
                "current_cycle", "total_cycles", "display_enabled", "cycle_type"
            ]
        }
        
        for node in nodes:
            node_type = node.get('type')
            node_params = node.get('params', {})
            
            print(f"\n--- {node_type} ---")
            
            if node_type in expected_params:
                expected = expected_params[node_type]
                available = list(node_params.keys())
                
                # Check which expected params are available
                found_params = [p for p in expected if p in available]
                missing_params = [p for p in expected if p not in available]
                extra_params = [p for p in available if p not in expected and not p.startswith(('uo_', 'wait_', 'error_', 'log_', 'description'))]
                
                print(f"  Expected params found: {len(found_params)}/{len(expected)}")
                if found_params:
                    print(f"    ✅ Found: {found_params}")
                if missing_params:
                    print(f"    ⚠️  Missing: {missing_params}")
                if extra_params:
                    print(f"    ➕ Extra: {extra_params[:5]}{'...' if len(extra_params) > 5 else ''}")
                
                # Test parameter value types
                for param in found_params[:3]:  # Test first 3 params
                    value = node_params[param]
                    print(f"    {param}: {type(value).__name__} = {value}")
            else:
                print(f"  ⚠️  No expected parameters defined for {node_type}")
                print(f"  Available params: {list(node_params.keys())[:5]}{'...' if len(node_params) > 5 else ''}")
        
        return True
        
    except Exception as e:
        print(f"❌ Parameter mapping test failed: {str(e)}")
        return False

def test_operation_coverage():
    """Test if all operations are covered in the mapper"""
    print("\n=== Testing Operation Coverage ===")
    
    try:
        # Load the new Canvas JSON
        with open('../data/test_workflow-1753364156528.json', 'r') as f:
            canvas_json = json.load(f)
        
        nodes = canvas_json['workflow']['nodes']
        
        # Extract all operation types from JSON
        json_operations = set(node.get('type') for node in nodes)
        
        # Define operations that should be in the mapper
        expected_mapper_operations = {
            "sdl1ExperimentSetup",
            "sdl1SolutionPreparation", 
            "sdl1ElectrodeSetup",
            "sdl1ElectrochemicalMeasurement",
            "sdl1WashCleaning",
            "sdl1DataExport",
            "sdl1SequenceControl",
            "sdl1CycleCounter"
        }
        
        print(f"Operations in JSON: {sorted(json_operations)}")
        print(f"Expected in mapper: {sorted(expected_mapper_operations)}")
        
        # Check coverage
        covered = json_operations & expected_mapper_operations
        missing = json_operations - expected_mapper_operations
        extra = expected_mapper_operations - json_operations
        
        print(f"\n📊 Coverage Analysis:")
        print(f"  ✅ Covered operations: {len(covered)}/{len(json_operations)}")
        if covered:
            print(f"    {sorted(covered)}")
        
        if missing:
            print(f"  ❌ Missing from mapper: {sorted(missing)}")
        
        if extra:
            print(f"  ➕ Extra in mapper: {sorted(extra)}")
        
        coverage_percentage = (len(covered) / len(json_operations)) * 100 if json_operations else 0
        print(f"\n📈 Coverage: {coverage_percentage:.1f}%")
        
        return len(missing) == 0
        
    except Exception as e:
        print(f"❌ Operation coverage test failed: {str(e)}")
        return False

def generate_compatibility_report():
    """Generate a compatibility report"""
    print("\n=== Compatibility Report ===")
    
    try:
        with open('../data/test_workflow-1753364156528.json', 'r') as f:
            canvas_json = json.load(f)
        
        nodes = canvas_json['workflow']['nodes']
        
        report = {
            "workflow_name": canvas_json['metadata']['name'],
            "workflow_id": canvas_json['metadata']['id'],
            "node_count": len(nodes),
            "operation_types": list(set(node.get('type') for node in nodes)),
            "total_parameters": sum(len(node.get('params', {})) for node in nodes),
            "new_format_features": []
        }
        
        # Check for new format features
        for node in nodes:
            if 'executionFlow' in node:
                report["new_format_features"].append("executionFlow")
                break
        
        for node in nodes:
            if 'metadata' in node and 'parameterGroups' in node['metadata']:
                report["new_format_features"].append("parameterGroups")
                break
        
        print(f"📋 Compatibility Report:")
        print(f"  Workflow: {report['workflow_name']} ({report['workflow_id']})")
        print(f"  Nodes: {report['node_count']}")
        print(f"  Operation types: {len(report['operation_types'])}")
        print(f"  Total parameters: {report['total_parameters']}")
        print(f"  New format features: {report['new_format_features']}")
        
        # Save report
        with open('compatibility_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        print(f"  📄 Report saved to compatibility_report.json")
        
        return True
        
    except Exception as e:
        print(f"❌ Report generation failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing JSON Format Compatibility")
    print("=" * 50)
    
    # Test JSON structure
    structure_ok = test_json_structure()
    
    # Test parameter mapping
    mapping_ok = test_parameter_mapping()
    
    # Test operation coverage
    coverage_ok = test_operation_coverage()
    
    # Generate report
    report_ok = generate_compatibility_report()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"JSON Structure: {'✅ PASS' if structure_ok else '❌ FAIL'}")
    print(f"Parameter Mapping: {'✅ PASS' if mapping_ok else '❌ FAIL'}")
    print(f"Operation Coverage: {'✅ PASS' if coverage_ok else '❌ FAIL'}")
    print(f"Report Generation: {'✅ PASS' if report_ok else '❌ FAIL'}")
    
    if structure_ok and mapping_ok and coverage_ok and report_ok:
        print("\n🎉 All tests passed! The new JSON format is compatible.")
    else:
        print("\n⚠️  Some tests failed. Check the details above.")
    
    return structure_ok and mapping_ok and coverage_ok and report_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
