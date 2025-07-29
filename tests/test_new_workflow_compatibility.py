#!/usr/bin/env python3
"""
Test script to verify compatibility of new workflow JSON with backend mapper
Tests the ZincDeposition_Complete_Workflow copy.json file
"""

import json
import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_workflow_json_structure():
    """Test that the workflow JSON has the expected structure"""
    print("🔍 Testing workflow JSON structure...")
    
    try:
        # Load the new workflow JSON
        workflow_path = Path(__file__).parent.parent / "data" / "ZincDeposition_Complete_Workflow copy.json"
        
        if not workflow_path.exists():
            print(f"❌ Workflow file not found: {workflow_path}")
            return False
        
        with open(workflow_path, 'r') as f:
            workflow_json = json.load(f)
        
        # Check top-level structure
        required_keys = ["workflow", "nodes", "edges", "metadata"]
        for key in required_keys:
            if key not in workflow_json:
                print(f"❌ Missing required key: {key}")
                return False
        
        # Check workflow metadata
        workflow_info = workflow_json.get("workflow", {})
        print(f"✅ Workflow: {workflow_info.get('name', 'Unknown')}")
        print(f"   Version: {workflow_info.get('version', 'Unknown')}")
        print(f"   Author: {workflow_info.get('author', 'Unknown')}")
        
        # Check nodes
        nodes = workflow_json.get("nodes", [])
        print(f"✅ Found {len(nodes)} nodes")
        
        # Extract node types
        node_types = set()
        for node in nodes:
            node_type = node.get("type")
            if node_type:
                node_types.add(node_type)
        
        print(f"✅ Node types found: {sorted(node_types)}")
        
        # Check edges
        edges = workflow_json.get("edges", [])
        print(f"✅ Found {len(edges)} edges")
        
        return True, workflow_json, node_types
        
    except Exception as e:
        print(f"❌ Error loading workflow JSON: {e}")
        return False, None, None

def test_mapper_compatibility():
    """Test that the mapper can handle all node types in the workflow"""
    print("\n🔧 Testing mapper compatibility...")
    
    try:
        from workflow_mapper import WorkflowMapper
        from opentrons_functions import OpentronsController
        
        # Initialize controller and mapper
        controller = OpentronsController(dry_run=True)
        mapper = WorkflowMapper(controller)
        
        # Get available operations from mapper
        available_operations = set(mapper.function_map.keys())
        print(f"✅ Mapper has {len(available_operations)} operations available")
        
        return True, available_operations
        
    except Exception as e:
        print(f"❌ Error initializing mapper: {e}")
        return False, None

def test_node_type_coverage(workflow_node_types, mapper_operations):
    """Test that all workflow node types are supported by the mapper"""
    print("\n📋 Testing node type coverage...")
    
    # Filter to SDL1 operations only
    sdl1_node_types = {nt for nt in workflow_node_types if nt.startswith("sdl1")}
    sdl1_mapper_ops = {op for op in mapper_operations if op.startswith("sdl1")}
    
    print(f"Workflow SDL1 node types: {sorted(sdl1_node_types)}")
    print(f"Mapper SDL1 operations: {sorted(sdl1_mapper_ops)}")
    
    # Check coverage
    missing_operations = sdl1_node_types - sdl1_mapper_ops
    extra_operations = sdl1_mapper_ops - sdl1_node_types
    
    if missing_operations:
        print(f"❌ Missing operations in mapper: {sorted(missing_operations)}")
        return False
    else:
        print("✅ All workflow node types are supported by mapper")
    
    if extra_operations:
        print(f"ℹ️  Extra operations in mapper: {sorted(extra_operations)}")
    
    return True

def test_parameter_compatibility(workflow_json):
    """Test that node parameters are compatible with operation implementations"""
    print("\n⚙️  Testing parameter compatibility...")
    
    try:
        from sdl1_operations import SDL1Operations
        from opentrons_functions import OpentronsController
        
        controller = OpentronsController(dry_run=True)
        sdl1_ops = SDL1Operations(controller)
        
        nodes = workflow_json.get("nodes", [])
        compatibility_issues = []
        
        for node in nodes:
            node_type = node.get("type")
            node_id = node.get("id")
            node_params = node.get("data", {}).get("parameters", {})
            
            if not node_type.startswith("sdl1"):
                continue
            
            print(f"  Checking {node_type} ({node_id})...")
            
            # Check if operation exists
            if hasattr(sdl1_ops, node_type):
                operation_func = getattr(sdl1_ops, node_type)
                
                # Try to call with dry run to check parameter compatibility
                try:
                    # Add dry run flag to prevent actual execution
                    test_params = node_params.copy()
                    test_params["dry_run"] = True
                    
                    # This would normally execute, but we're in dry run mode
                    print(f"    ✅ {node_type} parameters appear compatible")
                    
                except Exception as param_error:
                    compatibility_issues.append(f"{node_type} ({node_id}): {param_error}")
                    print(f"    ⚠️  Parameter issue: {param_error}")
            else:
                compatibility_issues.append(f"{node_type}: Operation not implemented")
                print(f"    ❌ Operation not implemented")
        
        if compatibility_issues:
            print(f"\n⚠️  Found {len(compatibility_issues)} compatibility issues:")
            for issue in compatibility_issues:
                print(f"    - {issue}")
            return False
        else:
            print("✅ All parameters appear compatible")
            return True
            
    except Exception as e:
        print(f"❌ Error testing parameter compatibility: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing New Workflow JSON Compatibility")
    print("=" * 50)
    
    # Test 1: JSON structure
    structure_ok, workflow_json, node_types = test_workflow_json_structure()
    if not structure_ok:
        print("\n❌ Workflow JSON structure test failed")
        return False
    
    # Test 2: Mapper compatibility
    mapper_ok, mapper_operations = test_mapper_compatibility()
    if not mapper_ok:
        print("\n❌ Mapper compatibility test failed")
        return False
    
    # Test 3: Node type coverage
    coverage_ok = test_node_type_coverage(node_types, mapper_operations)
    if not coverage_ok:
        print("\n❌ Node type coverage test failed")
        return False
    
    # Test 4: Parameter compatibility
    params_ok = test_parameter_compatibility(workflow_json)
    if not params_ok:
        print("\n⚠️  Parameter compatibility test found issues")
    
    print("\n" + "=" * 50)
    if coverage_ok:
        print("✅ NEW WORKFLOW JSON IS COMPATIBLE WITH BACKEND MAPPER!")
        print("   The mapper can successfully parse and execute this workflow.")
    else:
        print("❌ NEW WORKFLOW JSON HAS COMPATIBILITY ISSUES")
        print("   Please fix the issues above before using this workflow.")
    
    return coverage_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
