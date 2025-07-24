#!/usr/bin/env python3
"""
Prefect CLI for Battery SDL1

Command-line interface for managing Prefect workflows and deployments
for the SDL1 system.
"""

import asyncio
import json
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from prefect.client.orchestration import PrefectClient
    from prefect.server.api.server import create_app
    import uvicorn
    PREFECT_AVAILABLE = True
except ImportError:
    PREFECT_AVAILABLE = False

from .opentrons_functions import OpentronsController
from .prefect_deployment_manager import PrefectDeploymentManager
from .workflow_manager_factory import WorkflowManagerFactory


class PrefectCLI:
    """Command-line interface for Prefect workflow management"""
    
    def __init__(self):
        self.controller = OpentronsController(dry_run=True)
        if PREFECT_AVAILABLE:
            self.deployment_manager = PrefectDeploymentManager(self.controller)
        else:
            self.deployment_manager = None
    
    def check_prefect_availability(self):
        """Check if Prefect is available and configured"""
        if not PREFECT_AVAILABLE:
            print("❌ Prefect is not installed")
            print("Install with: pip install prefect>=2.10.0 prefect-shell>=0.1.0")
            return False
        
        print("✅ Prefect is available")
        return True
    
    async def start_prefect_server(self, host: str = "127.0.0.1", port: int = 4200):
        """Start a local Prefect server"""
        if not self.check_prefect_availability():
            return
        
        print(f"🚀 Starting Prefect server at http://{host}:{port}")
        print("📊 UI will be available at http://127.0.0.1:4200")
        print("🛑 Press Ctrl+C to stop")
        
        try:
            # Start the Prefect server
            from prefect.server.api.server import create_app
            app = create_app()
            
            config = uvicorn.Config(
                app=app,
                host=host,
                port=port,
                log_level="info"
            )
            server = uvicorn.Server(config)
            await server.serve()
            
        except KeyboardInterrupt:
            print("\n🛑 Prefect server stopped")
        except Exception as e:
            print(f"❌ Failed to start Prefect server: {str(e)}")
    
    async def deploy_workflow(
        self,
        workflow_file: str,
        deployment_name: str,
        schedule: Optional[str] = None
    ):
        """Deploy a workflow from a JSON file"""
        if not self.check_prefect_availability():
            return
        
        try:
            # Load workflow JSON
            workflow_path = Path(workflow_file)
            if not workflow_path.exists():
                print(f"❌ Workflow file not found: {workflow_file}")
                return
            
            with open(workflow_path, 'r') as f:
                workflow_json = json.load(f)
            
            print(f"📋 Deploying workflow: {deployment_name}")
            print(f"📄 From file: {workflow_file}")
            
            # Parse schedule if provided
            schedule_config = None
            if schedule:
                if schedule.startswith("interval:"):
                    # Format: interval:3600 (seconds)
                    interval_seconds = int(schedule.split(":")[1])
                    schedule_config = {
                        "type": "interval",
                        "interval_seconds": interval_seconds
                    }
                elif schedule.startswith("cron:"):
                    # Format: cron:0 9 * * * (daily at 9 AM)
                    cron_expression = schedule.split(":", 1)[1]
                    schedule_config = {
                        "type": "cron",
                        "cron": cron_expression
                    }
            
            # Create deployment
            deployment_id = await self.deployment_manager.create_workflow_deployment(
                workflow_name=deployment_name,
                workflow_json=workflow_json,
                schedule=schedule_config
            )
            
            print(f"✅ Deployment created successfully")
            print(f"🆔 Deployment ID: {deployment_id}")
            if schedule_config:
                print(f"⏰ Schedule: {schedule}")
            
        except Exception as e:
            print(f"❌ Deployment failed: {str(e)}")
    
    async def list_deployments(self):
        """List all SDL1 deployments"""
        if not self.check_prefect_availability():
            return
        
        try:
            deployments = await self.deployment_manager.list_deployments()
            
            if not deployments:
                print("📭 No SDL1 deployments found")
                return
            
            print(f"📋 Found {len(deployments)} SDL1 deployment(s):")
            print()
            
            for deployment in deployments:
                print(f"🔹 {deployment['name']}")
                print(f"   ID: {deployment['id']}")
                print(f"   Flow: {deployment['flow_name']}")
                print(f"   Schedule: {deployment['schedule'] or 'None'}")
                print(f"   Active: {deployment['is_schedule_active']}")
                print(f"   Created: {deployment['created']}")
                print()
                
        except Exception as e:
            print(f"❌ Failed to list deployments: {str(e)}")
    
    async def run_workflow(
        self,
        deployment_name: str,
        parameters: Optional[str] = None,
        scheduled_time: Optional[str] = None
    ):
        """Run a workflow deployment"""
        if not self.check_prefect_availability():
            return
        
        try:
            # Parse parameters if provided
            params = {}
            if parameters:
                params = json.loads(parameters)
            
            # Parse scheduled time if provided
            schedule_time = None
            if scheduled_time:
                schedule_time = datetime.fromisoformat(scheduled_time)
            
            if schedule_time:
                # Schedule for later execution
                flow_run_id = await self.deployment_manager.schedule_workflow_execution(
                    deployment_name=deployment_name,
                    scheduled_time=schedule_time,
                    parameters=params
                )
                print(f"⏰ Workflow scheduled for {schedule_time}")
                print(f"🆔 Flow run ID: {flow_run_id}")
            else:
                # Run immediately
                flow_run_id = await self.deployment_manager.schedule_workflow_execution(
                    deployment_name=deployment_name,
                    scheduled_time=datetime.now(),
                    parameters=params
                )
                print(f"🚀 Workflow started")
                print(f"🆔 Flow run ID: {flow_run_id}")
                
        except Exception as e:
            print(f"❌ Failed to run workflow: {str(e)}")
    
    async def get_workflow_status(self, flow_run_id: str):
        """Get the status of a workflow execution"""
        if not self.check_prefect_availability():
            return
        
        try:
            status = await self.deployment_manager.get_workflow_status(flow_run_id)
            
            print(f"📊 Workflow Status: {flow_run_id}")
            print(f"   Name: {status['name']}")
            print(f"   State: {status['state']}")
            if status['state_message']:
                print(f"   Message: {status['state_message']}")
            print(f"   Start Time: {status['start_time']}")
            print(f"   End Time: {status['end_time']}")
            print(f"   Duration: {status['total_run_time']}")
            
        except Exception as e:
            print(f"❌ Failed to get workflow status: {str(e)}")
    
    async def list_recent_runs(self, limit: int = 10):
        """List recent workflow executions"""
        if not self.check_prefect_availability():
            return
        
        try:
            runs = await self.deployment_manager.get_recent_flow_runs(limit)
            
            if not runs:
                print("📭 No recent workflow runs found")
                return
            
            print(f"📋 Recent {len(runs)} workflow run(s):")
            print()
            
            for run in runs:
                print(f"🔹 {run['name']}")
                print(f"   ID: {run['id']}")
                print(f"   Flow: {run['flow_name']}")
                print(f"   State: {run['state']}")
                print(f"   Start: {run['start_time']}")
                print(f"   Duration: {run['total_run_time']}")
                print()
                
        except Exception as e:
            print(f"❌ Failed to list recent runs: {str(e)}")
    
    def show_manager_comparison(self):
        """Show comparison between workflow managers"""
        managers = WorkflowManagerFactory.get_available_managers()
        
        print("🔄 Available Workflow Managers:")
        print()
        
        for manager_type, info in managers.items():
            status = "✅ Available" if info['available'] else "❌ Not Available"
            print(f"📦 {info['name']} ({manager_type})")
            print(f"   Status: {status}")
            print(f"   Description: {info['description']}")
            print(f"   Features:")
            for feature in info['features']:
                print(f"     • {feature}")
            print(f"   Requirements: {', '.join(info['requirements'])}")
            if not info['available'] and 'install_command' in info:
                print(f"   Install: {info['install_command']}")
            print()


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Prefect CLI for Battery SDL1 Workflow Management"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Server command
    server_parser = subparsers.add_parser('server', help='Start Prefect server')
    server_parser.add_argument('--host', default='127.0.0.1', help='Server host')
    server_parser.add_argument('--port', type=int, default=4200, help='Server port')
    
    # Deploy command
    deploy_parser = subparsers.add_parser('deploy', help='Deploy a workflow')
    deploy_parser.add_argument('workflow_file', help='Path to workflow JSON file')
    deploy_parser.add_argument('deployment_name', help='Name for the deployment')
    deploy_parser.add_argument('--schedule', help='Schedule (interval:3600 or cron:0 9 * * *)')
    
    # List deployments command
    subparsers.add_parser('list-deployments', help='List all deployments')
    
    # Run workflow command
    run_parser = subparsers.add_parser('run', help='Run a workflow')
    run_parser.add_argument('deployment_name', help='Name of the deployment')
    run_parser.add_argument('--parameters', help='JSON parameters for the workflow')
    run_parser.add_argument('--scheduled-time', help='Schedule time (ISO format)')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Get workflow status')
    status_parser.add_argument('flow_run_id', help='Flow run ID')
    
    # List runs command
    runs_parser = subparsers.add_parser('list-runs', help='List recent workflow runs')
    runs_parser.add_argument('--limit', type=int, default=10, help='Number of runs to show')
    
    # Compare managers command
    subparsers.add_parser('compare', help='Compare workflow managers')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = PrefectCLI()
    
    if args.command == 'server':
        asyncio.run(cli.start_prefect_server(args.host, args.port))
    elif args.command == 'deploy':
        asyncio.run(cli.deploy_workflow(args.workflow_file, args.deployment_name, args.schedule))
    elif args.command == 'list-deployments':
        asyncio.run(cli.list_deployments())
    elif args.command == 'run':
        asyncio.run(cli.run_workflow(args.deployment_name, args.parameters, args.scheduled_time))
    elif args.command == 'status':
        asyncio.run(cli.get_workflow_status(args.flow_run_id))
    elif args.command == 'list-runs':
        asyncio.run(cli.list_recent_runs(args.limit))
    elif args.command == 'compare':
        cli.show_manager_comparison()


if __name__ == "__main__":
    main()
