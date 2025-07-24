"""
Prefect Deployment Manager for Battery SDL1

This module handles deployment, scheduling, and management of Prefect workflows
for the SDL1 system.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

try:
    from prefect import flow
    from prefect.deployments import Deployment
    from prefect.server.schemas.schedules import IntervalSchedule, CronSchedule
    from prefect.infrastructure import Process
    from prefect.filesystems import LocalFileSystem
    from prefect.client.orchestration import PrefectClient
    PREFECT_AVAILABLE = True
except ImportError:
    PREFECT_AVAILABLE = False
    logging.warning("Prefect not available - deployment features disabled")

from .prefect_workflow_manager import PrefectWorkflowManager
from .opentrons_functions import OpentronsController


class PrefectDeploymentManager:
    """
    Manages Prefect deployments for SDL1 workflows
    Handles scheduling, monitoring, and deployment lifecycle
    """
    
    def __init__(self, controller: OpentronsController):
        self.controller = controller
        self.workflow_manager = PrefectWorkflowManager(controller)
        self.logger = logging.getLogger(__name__)
        
        if not PREFECT_AVAILABLE:
            raise ImportError("Prefect is required for deployment management")
    
    async def create_workflow_deployment(
        self,
        workflow_name: str,
        workflow_json: Dict[str, Any],
        schedule: Optional[Dict[str, Any]] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a Prefect deployment for a Canvas workflow
        
        Args:
            workflow_name: Name for the deployment
            workflow_json: Canvas workflow JSON
            schedule: Optional schedule configuration
            parameters: Optional default parameters
            
        Returns:
            Deployment ID
        """
        try:
            # Create the flow function
            @flow(name=f"SDL1 Workflow: {workflow_name}")
            def workflow_flow():
                return self.workflow_manager.execute_canvas_workflow_flow(workflow_json)
            
            # Configure schedule if provided
            deployment_schedule = None
            if schedule:
                schedule_type = schedule.get("type", "interval")
                if schedule_type == "interval":
                    interval_seconds = schedule.get("interval_seconds", 3600)
                    deployment_schedule = IntervalSchedule(interval=timedelta(seconds=interval_seconds))
                elif schedule_type == "cron":
                    cron_expression = schedule.get("cron", "0 9 * * *")  # Default: daily at 9 AM
                    deployment_schedule = CronSchedule(cron=cron_expression)
            
            # Create deployment
            deployment = Deployment.build_from_flow(
                flow=workflow_flow,
                name=workflow_name,
                schedule=deployment_schedule,
                parameters=parameters or {},
                infrastructure=Process(),
                storage=LocalFileSystem(basepath=str(Path.cwd())),
                work_queue_name="sdl1-workflows"
            )
            
            # Apply the deployment
            deployment_id = await deployment.apply()
            
            self.logger.info(f"Created deployment: {workflow_name} (ID: {deployment_id})")
            return deployment_id
            
        except Exception as e:
            self.logger.error(f"Failed to create deployment: {str(e)}")
            raise
    
    async def schedule_workflow_execution(
        self,
        deployment_name: str,
        scheduled_time: datetime,
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Schedule a workflow execution at a specific time
        
        Args:
            deployment_name: Name of the deployment
            scheduled_time: When to execute the workflow
            parameters: Optional parameters for the execution
            
        Returns:
            Flow run ID
        """
        try:
            async with PrefectClient() as client:
                # Find the deployment
                deployments = await client.read_deployments()
                deployment = next((d for d in deployments if d.name == deployment_name), None)
                
                if not deployment:
                    raise ValueError(f"Deployment not found: {deployment_name}")
                
                # Create a scheduled flow run
                flow_run = await client.create_flow_run_from_deployment(
                    deployment_id=deployment.id,
                    parameters=parameters or {},
                    scheduled_start_time=scheduled_time
                )
                
                self.logger.info(f"Scheduled workflow execution: {flow_run.id} at {scheduled_time}")
                return str(flow_run.id)
                
        except Exception as e:
            self.logger.error(f"Failed to schedule workflow: {str(e)}")
            raise
    
    async def get_workflow_status(self, flow_run_id: str) -> Dict[str, Any]:
        """
        Get the status of a workflow execution
        
        Args:
            flow_run_id: ID of the flow run
            
        Returns:
            Status information
        """
        try:
            async with PrefectClient() as client:
                flow_run = await client.read_flow_run(flow_run_id)
                
                return {
                    "id": str(flow_run.id),
                    "name": flow_run.name,
                    "state": flow_run.state.type if flow_run.state else "Unknown",
                    "state_message": flow_run.state.message if flow_run.state else None,
                    "start_time": flow_run.start_time.isoformat() if flow_run.start_time else None,
                    "end_time": flow_run.end_time.isoformat() if flow_run.end_time else None,
                    "total_run_time": str(flow_run.total_run_time) if flow_run.total_run_time else None,
                    "parameters": flow_run.parameters
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get workflow status: {str(e)}")
            raise
    
    async def cancel_workflow_execution(self, flow_run_id: str) -> bool:
        """
        Cancel a running workflow execution
        
        Args:
            flow_run_id: ID of the flow run to cancel
            
        Returns:
            True if successfully cancelled
        """
        try:
            async with PrefectClient() as client:
                await client.set_flow_run_state(
                    flow_run_id=flow_run_id,
                    state={"type": "CANCELLED", "message": "Cancelled by user"}
                )
                
                self.logger.info(f"Cancelled workflow execution: {flow_run_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to cancel workflow: {str(e)}")
            return False
    
    async def list_deployments(self) -> List[Dict[str, Any]]:
        """
        List all SDL1 workflow deployments
        
        Returns:
            List of deployment information
        """
        try:
            async with PrefectClient() as client:
                deployments = await client.read_deployments()
                
                sdl1_deployments = []
                for deployment in deployments:
                    if "SDL1" in deployment.name or "sdl1" in deployment.name.lower():
                        sdl1_deployments.append({
                            "id": str(deployment.id),
                            "name": deployment.name,
                            "flow_name": deployment.flow_name,
                            "schedule": str(deployment.schedule) if deployment.schedule else None,
                            "is_schedule_active": deployment.is_schedule_active,
                            "created": deployment.created.isoformat() if deployment.created else None,
                            "updated": deployment.updated.isoformat() if deployment.updated else None
                        })
                
                return sdl1_deployments
                
        except Exception as e:
            self.logger.error(f"Failed to list deployments: {str(e)}")
            return []
    
    async def get_recent_flow_runs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent workflow executions
        
        Args:
            limit: Maximum number of runs to return
            
        Returns:
            List of recent flow run information
        """
        try:
            async with PrefectClient() as client:
                flow_runs = await client.read_flow_runs(limit=limit)
                
                runs_info = []
                for run in flow_runs:
                    runs_info.append({
                        "id": str(run.id),
                        "name": run.name,
                        "flow_name": run.flow_name,
                        "state": run.state.type if run.state else "Unknown",
                        "start_time": run.start_time.isoformat() if run.start_time else None,
                        "end_time": run.end_time.isoformat() if run.end_time else None,
                        "total_run_time": str(run.total_run_time) if run.total_run_time else None
                    })
                
                return runs_info
                
        except Exception as e:
            self.logger.error(f"Failed to get recent flow runs: {str(e)}")
            return []
    
    def create_deployment_config(
        self,
        workflow_name: str,
        workflow_file: str,
        schedule_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a deployment configuration for a workflow file
        
        Args:
            workflow_name: Name for the deployment
            workflow_file: Path to the workflow JSON file
            schedule_config: Optional schedule configuration
            
        Returns:
            Deployment configuration
        """
        config = {
            "name": workflow_name,
            "workflow_file": workflow_file,
            "description": f"SDL1 workflow deployment for {workflow_name}",
            "tags": ["sdl1", "battery-research", "automation"],
            "parameters": {
                "dry_run": False,
                "save_results": True,
                "robot_ip": "169.254.69.185"
            }
        }
        
        if schedule_config:
            config["schedule"] = schedule_config
        
        return config
    
    async def deploy_from_config(self, config: Dict[str, Any]) -> str:
        """
        Deploy a workflow from a configuration dictionary
        
        Args:
            config: Deployment configuration
            
        Returns:
            Deployment ID
        """
        try:
            # Load workflow JSON
            workflow_file = config["workflow_file"]
            with open(workflow_file, 'r') as f:
                workflow_json = json.load(f)
            
            # Create deployment
            deployment_id = await self.create_workflow_deployment(
                workflow_name=config["name"],
                workflow_json=workflow_json,
                schedule=config.get("schedule"),
                parameters=config.get("parameters")
            )
            
            self.logger.info(f"Deployed workflow from config: {config['name']}")
            return deployment_id
            
        except Exception as e:
            self.logger.error(f"Failed to deploy from config: {str(e)}")
            raise
