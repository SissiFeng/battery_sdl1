#!/usr/bin/env python3
"""
Test script for API endpoints with new JSON format
Tests the API server's ability to handle the new Canvas JSON structure
"""

import json
import requests
import time
import sys
from datetime import datetime

def test_api_validation():
    """Test the API validation endpoint with new JSON format"""
    print("=== Testing API Validation Endpoint ===")
    
    try:
        # Load the new Canvas JSON
        with open('../data/test_workflow-1753364156528.json', 'r') as f:
            canvas_json = json.load(f)
        
        print(f"Loaded workflow: {canvas_json['metadata']['name']}")
        print(f"Nodes: {len(canvas_json['workflow']['nodes'])}")
        
        # Test validation endpoint
        print("Testing /canvas/validate endpoint...")
        response = requests.post(
            "http://localhost:8000/canvas/validate",
            json=canvas_json,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Validation successful")
            print(f"Valid: {result.get('validation', {}).get('valid', False)}")
            
            validation = result.get('validation', {})
            if validation.get('valid'):
                print(f"✅ Workflow is valid")
                print(f"Supported operations: {len(validation.get('supported_operations', []))}")
            else:
                print(f"❌ Validation failed")
                print(f"Errors: {validation.get('errors', [])}")
            
            return validation.get('valid', False)
        else:
            print(f"❌ Validation request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ API server not running. Start with: python api_server.py")
        return False
    except Exception as e:
        print(f"❌ Validation test failed: {str(e)}")
        return False

def test_api_dry_run():
    """Test the API dry-run execution with new JSON format"""
    print("\n=== Testing API Dry-Run Execution ===")
    
    try:
        # Load the new Canvas JSON
        with open('../data/test_workflow-1753364156528.json', 'r') as f:
            canvas_json = json.load(f)
        
        # Test dry-run execution
        print("Testing /canvas/execute/dry-run endpoint...")
        response = requests.post(
            "http://localhost:8000/canvas/execute/dry-run",
            json=canvas_json,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Dry-run execution successful")
            
            execution = result.get('execution', {})
            print(f"Status: {execution.get('status', 'unknown')}")
            print(f"Executed nodes: {execution.get('executed_nodes', 0)}")
            print(f"Successful nodes: {execution.get('successful_nodes', 0)}")
            print(f"Failed nodes: {len(execution.get('failed_nodes', []))}")
            
            if execution.get('failed_nodes'):
                print("Failed nodes:")
                for failed in execution.get('failed_nodes', []):
                    print(f"  - {failed}")
            
            return execution.get('status') == 'success'
        else:
            print(f"❌ Dry-run request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ API server not running. Start with: python api_server.py")
        return False
    except Exception as e:
        print(f"❌ Dry-run test failed: {str(e)}")
        return False

def test_api_status():
    """Test the API status endpoint"""
    print("\n=== Testing API Status ===")
    
    try:
        response = requests.get("http://localhost:8000/status", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API server is running")
            print(f"Status: {result.get('status', 'unknown')}")
            print(f"Version: {result.get('version', 'unknown')}")
            return True
        else:
            print(f"❌ Status request failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ API server not running")
        return False
    except Exception as e:
        print(f"❌ Status test failed: {str(e)}")
        return False

def test_individual_operations():
    """Test individual operations through the API"""
    print("\n=== Testing Individual Operations ===")
    
    try:
        # Load the new Canvas JSON
        with open('../data/test_workflow-1753364156528.json', 'r') as f:
            canvas_json = json.load(f)
        
        nodes = canvas_json['workflow']['nodes']
        
        # Test first few operations individually
        test_nodes = nodes[:3]  # Test first 3 nodes
        
        for i, node in enumerate(test_nodes):
            node_type = node.get('type')
            node_id = node.get('id')
            
            print(f"\n--- Testing {node_type} ---")
            
            # Create a single-node workflow for testing
            single_node_workflow = {
                "metadata": canvas_json['metadata'],
                "workflow": {
                    "nodes": [node],
                    "edges": [],
                    "executionMetadata": {}
                }
            }
            
            # Test validation for single node
            response = requests.post(
                "http://localhost:8000/canvas/validate",
                json=single_node_workflow,
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                validation = result.get('validation', {})
                if validation.get('valid'):
                    print(f"✅ {node_type} validation passed")
                else:
                    print(f"❌ {node_type} validation failed: {validation.get('errors', [])}")
            else:
                print(f"❌ {node_type} validation request failed")
        
        return True
        
    except Exception as e:
        print(f"❌ Individual operations test failed: {str(e)}")
        return False

def check_server_availability():
    """Check if the API server is available"""
    print("=== Checking API Server Availability ===")
    
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code in [200, 404]:  # 404 is OK, means server is running
            print("✅ API server is available")
            return True
        else:
            print(f"⚠️  API server responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ API server is not running")
        print("💡 To start the server, run: python api_server.py")
        return False
    except Exception as e:
        print(f"❌ Server check failed: {str(e)}")
        return False

def main():
    """Run all API tests"""
    print("🧪 Testing API with New Canvas JSON Format")
    print("=" * 50)
    
    # Check server availability first
    server_available = check_server_availability()
    
    if not server_available:
        print("\n❌ API server is not available. Cannot run API tests.")
        print("Please start the API server first with: python api_server.py")
        return False
    
    # Run API tests
    status_ok = test_api_status()
    validation_ok = test_api_validation()
    dry_run_ok = test_api_dry_run()
    operations_ok = test_individual_operations()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 API Test Summary:")
    print(f"Server Status: {'✅ PASS' if status_ok else '❌ FAIL'}")
    print(f"Validation: {'✅ PASS' if validation_ok else '❌ FAIL'}")
    print(f"Dry-Run Execution: {'✅ PASS' if dry_run_ok else '❌ FAIL'}")
    print(f"Individual Operations: {'✅ PASS' if operations_ok else '❌ FAIL'}")
    
    all_passed = status_ok and validation_ok and dry_run_ok and operations_ok
    
    if all_passed:
        print("\n🎉 All API tests passed! The API works with the new JSON format.")
    else:
        print("\n⚠️  Some API tests failed. Check the logs above for details.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
