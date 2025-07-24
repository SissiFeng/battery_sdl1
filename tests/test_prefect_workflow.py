#!/usr/bin/env python3
"""
Test script for Prefect workflow management

This script demonstrates the Prefect-based workflow management capabilities
for the SDL1 system.
"""

import json
import asyncio
import logging
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def test_prefect_availability():
    """Test if Prefect is available"""
    print("=== Testing Prefect Availability ===")
    
    try:
        import prefect
        print(f"✅ Prefect version: {prefect.__version__}")
        return True
    except ImportError:
        print("❌ Prefect not available")
        print("💡 Install with: pip install prefect>=2.10.0 prefect-shell>=0.1.0")
        return False

def test_workflow_manager_factory():
    """Test the workflow manager factory"""
    print("\n=== Testing Workflow Manager Factory ===")
    
    try:
        from workflow_manager_factory import WorkflowManagerFactory, WorkflowManagerType
        from opentrons_functions import OpentronsController
        
        # Test getting available managers
        managers = WorkflowManagerFactory.get_available_managers()
        print(f"Available managers: {list(managers.keys())}")
        
        for manager_type, info in managers.items():
            status = "✅ Available" if info['available'] else "❌ Not Available"
            print(f"  {manager_type}: {status}")
            print(f"    Features: {len(info['features'])} features")
        
        # Test creating native manager
        controller = OpentronsController(dry_run=True)
        native_manager = WorkflowManagerFactory.create_manager(
            WorkflowManagerType.NATIVE, controller
        )
        print(f"✅ Created native manager: {type(native_manager).__name__}")
        
        # Test creating Prefect manager (if available)
        if managers['prefect']['available']:
            prefect_manager = WorkflowManagerFactory.create_manager(
                WorkflowManagerType.PREFECT, controller
            )
            print(f"✅ Created Prefect manager: {type(prefect_manager).__name__}")
        else:
            print("⚠️  Prefect manager not available")
        
        return True
        
    except Exception as e:
        print(f"❌ Factory test failed: {str(e)}")
        return False

def test_unified_interface():
    """Test the unified workflow interface"""
    print("\n=== Testing Unified Workflow Interface ===")
    
    try:
        from workflow_manager_factory import UnifiedWorkflowInterface, WorkflowManagerType
        
        # Load test workflow
        workflow_file = Path("../data/test_workflow-1753364156528.json")
        if not workflow_file.exists():
            print(f"❌ Test workflow file not found: {workflow_file}")
            return False
        
        with open(workflow_file, 'r') as f:
            workflow_json = json.load(f)
        
        print(f"Loaded workflow: {workflow_json['metadata']['name']}")
        
        # Test with native manager
        print("\n--- Testing Native Manager ---")
        native_interface = UnifiedWorkflowInterface(
            manager_type=WorkflowManagerType.NATIVE
        )
        
        print(f"Manager info: {native_interface.get_manager_info()}")
        
        result = native_interface.execute_workflow(workflow_json)
        print(f"Native execution: {result.get('status')} - {result.get('successful_nodes', 0)} nodes")
        
        # Test with Prefect manager (if available)
        try:
            print("\n--- Testing Prefect Manager ---")
            prefect_interface = UnifiedWorkflowInterface(
                manager_type=WorkflowManagerType.PREFECT
            )
            
            print(f"Manager info: {prefect_interface.get_manager_info()}")
            
            result = prefect_interface.execute_workflow(workflow_json)
            print(f"Prefect execution: {result.get('status')} - {result.get('successful_nodes', 0)} nodes")
            
        except ImportError:
            print("⚠️  Prefect interface not available")
        
        return True
        
    except Exception as e:
        print(f"❌ Unified interface test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_prefect_deployment_manager():
    """Test Prefect deployment management"""
    print("\n=== Testing Prefect Deployment Manager ===")
    
    try:
        from prefect_deployment_manager import PrefectDeploymentManager
        from opentrons_functions import OpentronsController
        
        controller = OpentronsController(dry_run=True)
        deployment_manager = PrefectDeploymentManager(controller)
        
        print("✅ Created Prefect deployment manager")
        
        # Test deployment configuration
        config = deployment_manager.create_deployment_config(
            workflow_name="Test SDL1 Workflow",
            workflow_file="../data/test_workflow-1753364156528.json",
            schedule_config={
                "type": "interval",
                "interval_seconds": 3600  # Every hour
            }
        )
        
        print(f"✅ Created deployment config: {config['name']}")
        print(f"   Schedule: {config.get('schedule', 'None')}")
        
        # Note: We don't actually deploy to avoid requiring a running Prefect server
        print("⚠️  Skipping actual deployment (requires Prefect server)")
        
        return True
        
    except ImportError:
        print("❌ Prefect deployment manager not available")
        return False
    except Exception as e:
        print(f"❌ Deployment manager test failed: {str(e)}")
        return False

def test_manager_recommendations():
    """Test manager recommendation system"""
    print("\n=== Testing Manager Recommendations ===")
    
    try:
        from workflow_manager_factory import WorkflowManagerFactory
        
        use_cases = ["basic", "production", "research", "development"]
        
        for use_case in use_cases:
            recommendation = WorkflowManagerFactory.recommend_manager(use_case)
            print(f"\n{use_case.title()} use case:")
            print(f"  Recommended: {recommendation['recommended']}")
            print(f"  Reasoning: {recommendation['reasoning']}")
            if recommendation.get('alternative'):
                print(f"  Alternative: {recommendation['alternative']}")
            if recommendation.get('suggestion'):
                print(f"  Suggestion: {recommendation['suggestion']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Recommendation test failed: {str(e)}")
        return False

def test_cli_functionality():
    """Test CLI functionality (without actually running commands)"""
    print("\n=== Testing CLI Functionality ===")
    
    try:
        from prefect_cli import PrefectCLI
        
        cli = PrefectCLI()
        print("✅ Created Prefect CLI instance")
        
        # Test availability check
        available = cli.check_prefect_availability()
        print(f"Prefect availability: {available}")
        
        # Test manager comparison
        cli.show_manager_comparison()
        
        return True
        
    except Exception as e:
        print(f"❌ CLI test failed: {str(e)}")
        return False

def main():
    """Run all Prefect workflow tests"""
    print("🧪 Testing Prefect Workflow Management for SDL1")
    print("=" * 60)
    
    # Run tests
    tests = [
        ("Prefect Availability", test_prefect_availability),
        ("Workflow Manager Factory", test_workflow_manager_factory),
        ("Unified Interface", test_unified_interface),
        ("Manager Recommendations", test_manager_recommendations),
        ("CLI Functionality", test_cli_functionality)
    ]
    
    # Add async test
    async_tests = [
        ("Prefect Deployment Manager", test_prefect_deployment_manager)
    ]
    
    results = []
    
    # Run synchronous tests
    for test_name, test_func in tests:
        print(f"\n{'='*40}")
        print(f"Running: {test_name}")
        print(f"{'='*40}")
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
            results.append((test_name, False))
    
    # Run async tests
    for test_name, test_func in async_tests:
        print(f"\n{'='*40}")
        print(f"Running: {test_name}")
        print(f"{'='*40}")
        
        try:
            result = asyncio.run(test_func())
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 Test Summary")
    print(f"{'='*60}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"Total tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success rate: {(passed/total*100):.1f}%")
    
    print(f"\n📋 Individual Results:")
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} | {test_name}")
    
    if passed == total:
        print(f"\n🎉 All tests passed! Prefect workflow management is working correctly.")
    else:
        print(f"\n⚠️  Some tests failed. Check the details above.")
        if not test_prefect_availability():
            print(f"\n💡 Install Prefect to enable all features:")
            print(f"   pip install prefect>=2.10.0 prefect-shell>=0.1.0")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
