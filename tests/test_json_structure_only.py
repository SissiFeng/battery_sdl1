#!/usr/bin/env python3
"""
Simplified test script to verify JSON structure and operation mapping
without requiring external dependencies
"""

import json
import sys
from pathlib import Path

def test_workflow_json_structure():
    """Test that the workflow JSON has the expected structure"""
    print("🔍 Testing workflow JSON structure...")
    
    try:
        # Load the new workflow JSON
        workflow_path = Path(__file__).parent.parent / "data" / "ZincDeposition_Complete_Workflow copy.json"
        
        if not workflow_path.exists():
            print(f"❌ Workflow file not found: {workflow_path}")
            return False, None, None
        
        with open(workflow_path, 'r') as f:
            workflow_json = json.load(f)
        
        # Check top-level structure
        required_keys = ["workflow", "nodes", "edges", "metadata"]
        for key in required_keys:
            if key not in workflow_json:
                print(f"❌ Missing required key: {key}")
                return False, None, None
        
        # Check workflow metadata
        workflow_info = workflow_json.get("workflow", {})
        print(f"✅ Workflow: {workflow_info.get('name', 'Unknown')}")
        print(f"   Version: {workflow_info.get('version', 'Unknown')}")
        print(f"   Author: {workflow_info.get('author', 'Unknown')}")
        
        # Check nodes
        nodes = workflow_json.get("nodes", [])
        print(f"✅ Found {len(nodes)} nodes")
        
        # Extract node types and their details
        node_types = set()
        node_details = []
        for node in nodes:
            node_type = node.get("type")
            node_id = node.get("id")
            if node_type:
                node_types.add(node_type)
                node_details.append({
                    "id": node_id,
                    "type": node_type,
                    "label": node.get("data", {}).get("label", "Unknown")
                })
        
        print(f"✅ Node types found: {sorted(node_types)}")
        
        # Print node details
        print("\n📋 Node Details:")
        for detail in node_details:
            print(f"   - {detail['type']}: {detail['label']} ({detail['id']})")
        
        # Check edges
        edges = workflow_json.get("edges", [])
        print(f"\n✅ Found {len(edges)} edges")
        
        return True, workflow_json, node_types
        
    except Exception as e:
        print(f"❌ Error loading workflow JSON: {e}")
        return False, None, None

def check_mapper_operations():
    """Check what operations are defined in the mapper without importing"""
    print("\n🔧 Checking mapper operations...")
    
    try:
        # Read the workflow_mapper.py file to extract operation mappings
        mapper_path = Path(__file__).parent.parent / "src" / "workflow_mapper.py"
        
        if not mapper_path.exists():
            print(f"❌ Mapper file not found: {mapper_path}")
            return False, None
        
        with open(mapper_path, 'r') as f:
            mapper_content = f.read()
        
        # Extract SDL1 operations from the function map
        sdl1_operations = set()
        lines = mapper_content.split('\n')
        in_function_map = False
        
        for line in lines:
            line = line.strip()
            if '"sdl1' in line and '":' in line and 'self.sdl1_ops.sdl1' in line:
                # Extract operation name - only from function map entries
                start = line.find('"sdl1')
                end = line.find('"', start + 1)
                if start != -1 and end != -1:
                    operation = line[start+1:end]
                    # Only add if it's a real operation (not a method call)
                    if operation.startswith('sdl1') and not '_' in operation[4:]:
                        sdl1_operations.add(operation)
        
        print(f"✅ Found {len(sdl1_operations)} SDL1 operations in mapper:")
        for op in sorted(sdl1_operations):
            print(f"   - {op}")
        
        return True, sdl1_operations
        
    except Exception as e:
        print(f"❌ Error reading mapper file: {e}")
        return False, None

def check_sdl1_operations_implementation():
    """Check what operations are implemented in SDL1Operations"""
    print("\n🔧 Checking SDL1Operations implementation...")
    
    try:
        # Read the sdl1_operations.py file to extract implemented methods
        sdl1_path = Path(__file__).parent.parent / "src" / "sdl1_operations.py"
        
        if not sdl1_path.exists():
            print(f"❌ SDL1Operations file not found: {sdl1_path}")
            return False, None
        
        with open(sdl1_path, 'r') as f:
            sdl1_content = f.read()
        
        # Extract SDL1 method definitions
        implemented_operations = set()
        lines = sdl1_content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('def sdl1') and '(' in line:
                # Extract method name
                start = line.find('def ') + 4
                end = line.find('(')
                if start != -1 and end != -1:
                    method_name = line[start:end]
                    implemented_operations.add(method_name)
        
        print(f"✅ Found {len(implemented_operations)} SDL1 operations implemented:")
        for op in sorted(implemented_operations):
            print(f"   - {op}")
        
        return True, implemented_operations
        
    except Exception as e:
        print(f"❌ Error reading SDL1Operations file: {e}")
        return False, None

def test_operation_coverage(workflow_node_types, mapper_operations, implemented_operations):
    """Test that all workflow node types are covered"""
    print("\n📋 Testing operation coverage...")
    
    # Filter to SDL1 operations only
    sdl1_node_types = {nt for nt in workflow_node_types if nt.startswith("sdl1")}
    
    print(f"\nWorkflow requires: {sorted(sdl1_node_types)}")
    print(f"Mapper provides: {sorted(mapper_operations)}")
    print(f"Implementation has: {sorted(implemented_operations)}")
    
    # Check mapper coverage
    missing_in_mapper = sdl1_node_types - mapper_operations
    if missing_in_mapper:
        print(f"\n❌ Missing in mapper: {sorted(missing_in_mapper)}")
        return False
    else:
        print(f"\n✅ All workflow operations are mapped")
    
    # Check implementation coverage
    missing_in_implementation = mapper_operations - implemented_operations
    if missing_in_implementation:
        print(f"❌ Missing in implementation: {sorted(missing_in_implementation)}")
        return False
    else:
        print(f"✅ All mapped operations are implemented")
    
    return True

def main():
    """Main test function"""
    print("🧪 Testing New Workflow JSON Compatibility (Structure Only)")
    print("=" * 60)
    
    # Test 1: JSON structure
    structure_ok, workflow_json, node_types = test_workflow_json_structure()
    if not structure_ok:
        print("\n❌ Workflow JSON structure test failed")
        return False
    
    # Test 2: Mapper operations
    mapper_ok, mapper_operations = check_mapper_operations()
    if not mapper_ok:
        print("\n❌ Mapper operations check failed")
        return False
    
    # Test 3: Implementation check
    impl_ok, implemented_operations = check_sdl1_operations_implementation()
    if not impl_ok:
        print("\n❌ Implementation check failed")
        return False
    
    # Test 4: Coverage
    coverage_ok = test_operation_coverage(node_types, mapper_operations, implemented_operations)
    
    print("\n" + "=" * 60)
    if coverage_ok:
        print("✅ NEW WORKFLOW JSON IS COMPATIBLE WITH BACKEND MAPPER!")
        print("   All required operations are mapped and implemented.")
        print("   The workflow should execute successfully.")
    else:
        print("❌ NEW WORKFLOW JSON HAS COMPATIBILITY ISSUES")
        print("   Please fix the missing operations before using this workflow.")
    
    return coverage_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
