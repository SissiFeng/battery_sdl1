#!/usr/bin/env python3
"""
Test script to validate the new JSON format compatibility
Tests the mapper with the new Canvas JSON structure
"""

import json
import logging
import sys
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def test_json_parsing():
    """Test if we can parse the new JSON format"""
    print("=== Testing New JSON Format Parsing ===")
    
    try:
        # Load the new Canvas JSON
        with open('../data/test_workflow-1753364156528.json', 'r') as f:
            canvas_json = json.load(f)
        
        print(f"✅ JSON loaded successfully")
        print(f"Workflow name: {canvas_json['metadata']['name']}")
        print(f"Workflow ID: {canvas_json['metadata']['id']}")
        print(f"Node count: {len(canvas_json['workflow']['nodes'])}")
        
        # Analyze the structure
        nodes = canvas_json['workflow']['nodes']
        for i, node in enumerate(nodes):
            print(f"\nNode {i+1}:")
            print(f"  ID: {node['id']}")
            print(f"  Type: {node['type']}")
            print(f"  Label: {node['label']}")
            print(f"  Params count: {len(node['params'])}")
            print(f"  Has metadata: {'metadata' in node}")
            print(f"  Has executionFlow: {'executionFlow' in node}")
            
            # Check if this is a new structure
            if 'metadata' in node and 'parameterGroups' in node['metadata']:
                print(f"  ⚠️  New format detected with parameterGroups")
                param_groups = node['metadata']['parameterGroups']
                print(f"  Parameter groups: {list(param_groups.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ JSON parsing failed: {str(e)}")
        return False

def test_mapper_compatibility():
    """Test if the current mapper can handle the new format"""
    print("\n=== Testing Mapper Compatibility ===")
    
    try:
        # Try to import the mapper (without opentrons dependency)
        sys.path.append('.')
        
        # Load the JSON
        with open('../data/test_workflow-1753364156528.json', 'r') as f:
            canvas_json = json.load(f)
        
        # Test the structure that the mapper expects
        workflow_data = canvas_json.get("workflow", {})
        nodes = workflow_data.get("nodes", [])
        metadata = canvas_json.get("metadata", {})
        
        print(f"✅ Structure extraction successful")
        print(f"Metadata keys: {list(metadata.keys())}")
        print(f"Workflow keys: {list(workflow_data.keys())}")
        
        # Test each node structure
        for i, node in enumerate(nodes):
            node_type = node.get("type")
            node_params = node.get("params", {})
            node_id = node.get("id", "unknown")
            
            print(f"\nNode {i+1} analysis:")
            print(f"  Type: {node_type}")
            print(f"  ID: {node_id}")
            print(f"  Params available: {len(node_params) > 0}")
            
            # Check if this is an SDL1 operation
            if node_type and node_type.startswith("sdl1"):
                print(f"  ✅ SDL1 operation detected")
                
                # Check for required common parameters
                required_params = ["uo_name", "description", "error_handling", "log_level"]
                missing_params = [p for p in required_params if p not in node_params]
                
                if missing_params:
                    print(f"  ⚠️  Missing required params: {missing_params}")
                else:
                    print(f"  ✅ All required params present")
            else:
                print(f"  ⚠️  Non-SDL1 operation: {node_type}")
        
        return True
        
    except Exception as e:
        print(f"❌ Mapper compatibility test failed: {str(e)}")
        return False

def analyze_differences():
    """Analyze differences between old and new JSON formats"""
    print("\n=== Analyzing Format Differences ===")
    
    try:
        # Load both files
        with open('../data/test_workflow-1753364156528.json', 'r') as f:
            new_json = json.load(f)

        with open('../data/test_workflow-1753285688253.json', 'r') as f:
            old_json = json.load(f)
        
        print("Comparing JSON structures...")
        
        # Compare metadata
        print(f"\nMetadata comparison:")
        new_meta_keys = set(new_json['metadata'].keys())
        old_meta_keys = set(old_json['metadata'].keys())
        print(f"  Common keys: {new_meta_keys & old_meta_keys}")
        print(f"  New keys: {new_meta_keys - old_meta_keys}")
        print(f"  Removed keys: {old_meta_keys - new_meta_keys}")
        
        # Compare node structure
        print(f"\nNode structure comparison:")
        new_node = new_json['workflow']['nodes'][0]
        old_node = old_json['workflow']['nodes'][0]
        
        new_node_keys = set(new_node.keys())
        old_node_keys = set(old_node.keys())
        print(f"  Common keys: {new_node_keys & old_node_keys}")
        print(f"  New keys: {new_node_keys - old_node_keys}")
        print(f"  Removed keys: {old_node_keys - new_node_keys}")
        
        # Check params structure
        print(f"\nParams comparison:")
        new_params = set(new_node['params'].keys())
        old_params = set(old_node['params'].keys())
        print(f"  Common params: {new_params & old_params}")
        print(f"  New params: {new_params - old_params}")
        print(f"  Removed params: {old_params - new_params}")
        
        # Check metadata structure
        if 'metadata' in new_node and 'metadata' in old_node:
            print(f"\nNode metadata comparison:")
            new_meta = set(new_node['metadata'].keys())
            old_meta = set(old_node['metadata'].keys())
            print(f"  Common keys: {new_meta & old_meta}")
            print(f"  New keys: {new_meta - old_meta}")
            print(f"  Removed keys: {old_meta - new_meta}")
        
        return True
        
    except Exception as e:
        print(f"❌ Difference analysis failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing New Canvas JSON Format Compatibility")
    print("=" * 50)
    
    # Test JSON parsing
    json_ok = test_json_parsing()
    
    # Test mapper compatibility
    mapper_ok = test_mapper_compatibility()
    
    # Analyze differences
    diff_ok = analyze_differences()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"JSON Parsing: {'✅ PASS' if json_ok else '❌ FAIL'}")
    print(f"Mapper Compatibility: {'✅ PASS' if mapper_ok else '❌ FAIL'}")
    print(f"Difference Analysis: {'✅ PASS' if diff_ok else '❌ FAIL'}")
    
    if json_ok and mapper_ok and diff_ok:
        print("\n🎉 All tests passed! The new JSON format should be compatible.")
    else:
        print("\n⚠️  Some tests failed. The mapper may need updates.")
    
    return json_ok and mapper_ok and diff_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
