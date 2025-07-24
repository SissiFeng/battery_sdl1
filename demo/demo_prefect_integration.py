#!/usr/bin/env python3
"""
Demo script for Prefect Integration with Battery SDL1

This script demonstrates how to use the Prefect workflow management system
as an alternative to the native workflow manager.
"""

import json
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def check_prefect_availability():
    """Check if Prefect is available"""
    try:
        import prefect
        print(f"✅ Prefect {prefect.__version__} is available")
        return True
    except ImportError:
        print("❌ Prefect is not installed")
        print("💡 To install Prefect:")
        print("   pip install prefect>=2.10.0 prefect-shell>=0.1.0")
        return False

def demo_workflow_manager_factory():
    """Demonstrate the workflow manager factory"""
    print("\n" + "="*60)
    print("🏭 Workflow Manager Factory Demo")
    print("="*60)
    
    try:
        from workflow_manager_factory import WorkflowManagerFactory
        
        # Get available managers
        managers = WorkflowManagerFactory.get_available_managers()
        
        print("📋 Available Workflow Managers:")
        for manager_type, info in managers.items():
            status = "✅ Available" if info['available'] else "❌ Not Available"
            print(f"\n🔹 {info['name']} ({manager_type})")
            print(f"   Status: {status}")
            print(f"   Description: {info['description']}")
            print(f"   Features ({len(info['features'])}):")
            for feature in info['features'][:3]:  # Show first 3 features
                print(f"     • {feature}")
            if len(info['features']) > 3:
                print(f"     • ... and {len(info['features']) - 3} more")
            
            if not info['available'] and 'install_command' in info:
                print(f"   📦 Install: {info['install_command']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        return False

def demo_manager_recommendations():
    """Demonstrate manager recommendations"""
    print("\n" + "="*60)
    print("💡 Manager Recommendation Demo")
    print("="*60)
    
    try:
        from workflow_manager_factory import WorkflowManagerFactory
        
        use_cases = [
            ("basic", "Simple workflow execution for testing"),
            ("production", "Reliable production environment"),
            ("research", "Flexible research and experimentation"),
            ("development", "Development with debugging needs")
        ]
        
        for use_case, description in use_cases:
            print(f"\n🎯 {use_case.title()} Use Case: {description}")
            
            recommendation = WorkflowManagerFactory.recommend_manager(use_case)
            print(f"   Recommended: {recommendation['recommended']}")
            print(f"   Reasoning: {recommendation['reasoning']}")
            
            if recommendation.get('alternative'):
                print(f"   Alternative: {recommendation['alternative']}")
            if recommendation.get('suggestion'):
                print(f"   💡 {recommendation['suggestion']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        return False

def demo_unified_interface():
    """Demonstrate the unified workflow interface"""
    print("\n" + "="*60)
    print("🔄 Unified Workflow Interface Demo")
    print("="*60)
    
    try:
        from workflow_manager_factory import UnifiedWorkflowInterface, WorkflowManagerType
        
        # Check if test workflow exists
        workflow_file = Path("data/test_workflow-1753364156528.json")
        if not workflow_file.exists():
            print(f"❌ Test workflow not found: {workflow_file}")
            print("💡 Make sure you're running from the repository root")
            return False
        
        # Load test workflow
        with open(workflow_file, 'r') as f:
            workflow_json = json.load(f)
        
        workflow_name = workflow_json['metadata']['name']
        node_count = len(workflow_json['workflow']['nodes'])
        
        print(f"📄 Loaded workflow: {workflow_name}")
        print(f"📊 Nodes: {node_count}")
        
        # Demo with native manager
        print(f"\n--- Native Manager Demo ---")
        try:
            native_interface = UnifiedWorkflowInterface(
                manager_type=WorkflowManagerType.NATIVE
            )
            
            manager_info = native_interface.get_manager_info()
            print(f"Manager: {manager_info['class']}")
            print(f"Features: {len(manager_info['features'])} available")
            
            # Execute workflow
            print("🚀 Executing workflow with native manager...")
            result = native_interface.execute_workflow(workflow_json)
            
            print(f"✅ Execution completed")
            print(f"   Status: {result.get('status')}")
            print(f"   Successful nodes: {result.get('successful_nodes', 0)}/{node_count}")
            
            if result.get('failed_nodes'):
                print(f"   Failed nodes: {len(result.get('failed_nodes', []))}")
            
        except Exception as e:
            print(f"❌ Native manager demo failed: {str(e)}")
        
        # Demo with Prefect manager (if available)
        print(f"\n--- Prefect Manager Demo ---")
        try:
            prefect_interface = UnifiedWorkflowInterface(
                manager_type=WorkflowManagerType.PREFECT
            )
            
            manager_info = prefect_interface.get_manager_info()
            print(f"Manager: {manager_info['class']}")
            print(f"Features: {len(manager_info['features'])} available")
            
            # Execute workflow
            print("🚀 Executing workflow with Prefect manager...")
            result = prefect_interface.execute_workflow(workflow_json)
            
            print(f"✅ Execution completed")
            print(f"   Status: {result.get('status')}")
            print(f"   Successful nodes: {result.get('successful_nodes', 0)}/{node_count}")
            
            if result.get('failed_nodes'):
                print(f"   Failed nodes: {len(result.get('failed_nodes', []))}")
            
        except ImportError:
            print("⚠️  Prefect manager not available (Prefect not installed)")
        except Exception as e:
            print(f"❌ Prefect manager demo failed: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def demo_api_integration():
    """Demonstrate API integration"""
    print("\n" + "="*60)
    print("🌐 API Integration Demo")
    print("="*60)
    
    print("📡 API Endpoints for Workflow Management:")
    print()
    
    endpoints = [
        ("GET /managers", "Get available workflow managers"),
        ("POST /managers/configure", "Configure workflow manager type"),
        ("POST /canvas/execute", "Execute workflow with configured manager"),
        ("POST /canvas/execute/dry-run", "Dry-run execution"),
        ("POST /canvas/validate", "Validate workflow")
    ]
    
    for endpoint, description in endpoints:
        print(f"  🔹 {endpoint}")
        print(f"     {description}")
    
    print(f"\n💡 Example API Usage:")
    print(f"   # Configure Prefect manager")
    print(f"   curl -X POST http://localhost:8000/managers/configure \\")
    print(f"     -H 'Content-Type: application/json' \\")
    print(f"     -d '{{\"manager_type\": \"prefect\", \"dry_run\": true}}'")
    print(f"")
    print(f"   # Check available managers")
    print(f"   curl http://localhost:8000/managers")
    
    return True

def demo_cli_commands():
    """Demonstrate CLI commands"""
    print("\n" + "="*60)
    print("⌨️  CLI Commands Demo")
    print("="*60)
    
    print("🔧 Prefect CLI Commands:")
    print()
    
    commands = [
        ("server", "Start Prefect server with web UI"),
        ("deploy <workflow.json> <name>", "Deploy a workflow"),
        ("list-deployments", "List all deployments"),
        ("run <deployment-name>", "Run a workflow"),
        ("status <flow-run-id>", "Check workflow status"),
        ("list-runs", "List recent workflow runs"),
        ("compare", "Compare workflow managers")
    ]
    
    for command, description in commands:
        print(f"  🔹 python src/prefect_cli.py {command}")
        print(f"     {description}")
    
    print(f"\n💡 Example CLI Usage:")
    print(f"   # Start Prefect server")
    print(f"   python src/prefect_cli.py server")
    print(f"")
    print(f"   # Deploy workflow with hourly schedule")
    print(f"   python src/prefect_cli.py deploy \\")
    print(f"     data/test_workflow-1753364156528.json \\")
    print(f"     \"Hourly SDL1 Workflow\" \\")
    print(f"     --schedule \"interval:3600\"")
    print(f"")
    print(f"   # Compare managers")
    print(f"   python src/prefect_cli.py compare")
    
    return True

def main():
    """Run the Prefect integration demo"""
    print("🧪 Battery SDL1 - Prefect Integration Demo")
    print("=" * 80)
    print("This demo shows how to use Prefect as an alternative workflow manager")
    print("for enhanced task orchestration, monitoring, and scheduling.")
    print()
    
    # Check Prefect availability
    prefect_available = check_prefect_availability()
    
    # Run demos
    demos = [
        ("Workflow Manager Factory", demo_workflow_manager_factory),
        ("Manager Recommendations", demo_manager_recommendations),
        ("Unified Interface", demo_unified_interface),
        ("API Integration", demo_api_integration),
        ("CLI Commands", demo_cli_commands)
    ]
    
    results = []
    
    for demo_name, demo_func in demos:
        try:
            result = demo_func()
            results.append((demo_name, result))
        except Exception as e:
            print(f"❌ Demo '{demo_name}' failed: {str(e)}")
            results.append((demo_name, False))
    
    # Summary
    print("\n" + "="*80)
    print("📊 Demo Summary")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"Total demos: {total}")
    print(f"Successful: {passed}")
    print(f"Failed: {total - passed}")
    
    print(f"\n📋 Demo Results:")
    for demo_name, result in results:
        status = "✅ SUCCESS" if result else "❌ FAILED"
        print(f"  {status} | {demo_name}")
    
    print(f"\n🎯 Next Steps:")
    if not prefect_available:
        print(f"  1. Install Prefect: pip install prefect>=2.10.0 prefect-shell>=0.1.0")
        print(f"  2. Re-run this demo to see Prefect features")
    else:
        print(f"  1. Start Prefect server: python src/prefect_cli.py server")
        print(f"  2. Deploy a workflow: python src/prefect_cli.py deploy ...")
        print(f"  3. Monitor workflows at http://127.0.0.1:4200")
    
    print(f"  4. Read the guide: docs/PREFECT_WORKFLOW_GUIDE.md")
    print(f"  5. Try the API endpoints with your workflows")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
