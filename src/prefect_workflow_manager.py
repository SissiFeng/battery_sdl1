"""
Prefect-based Workflow Manager for Battery SDL1

This module provides an alternative workflow management system using Prefect
for enhanced task orchestration, monitoring, and scheduling capabilities.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

try:
    from prefect import flow, task, get_run_logger
    from prefect.task_runners import ConcurrentTaskRunner, SequentialTaskRunner
    from prefect.blocks.system import Secret
    from prefect.deployments import Deployment
    from prefect.server.schemas.schedules import IntervalSchedule
    PREFECT_AVAILABLE = True
except ImportError:
    PREFECT_AVAILABLE = False
    logging.warning("Prefect not available - falling back to basic workflow management")

from .opentrons_functions import OpentronsController
from .sdl1_operations import SDL1Operations


class PrefectWorkflowManager:
    """
    Prefect-based workflow manager for SDL1 operations
    Provides advanced task orchestration, monitoring, and scheduling
    """
    
    def __init__(self, controller: OpentronsController):
        self.controller = controller
        self.sdl1_ops = SDL1Operations(controller)
        self.logger = logging.getLogger(__name__)
        
        if not PREFECT_AVAILABLE:
            raise ImportError("Prefect is required for PrefectWorkflowManager. Install with: pip install prefect")
    
    @task(name="SDL1 Experiment Setup", retries=2, retry_delay_seconds=30)
    def experiment_setup_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Prefect task for experiment setup"""
        logger = get_run_logger()
        logger.info(f"Starting experiment setup: {params.get('experiment_id', 'Unknown')}")
        
        try:
            result = self.sdl1_ops.sdl1ExperimentSetup(params)
            logger.info(f"Experiment setup completed: {result.get('status')}")
            return result
        except Exception as e:
            logger.error(f"Experiment setup failed: {str(e)}")
            raise
    
    @task(name="SDL1 Solution Preparation", retries=1, retry_delay_seconds=15)
    def solution_preparation_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Prefect task for solution preparation"""
        logger = get_run_logger()
        logger.info(f"Preparing solution: {params.get('volume', 0)}μL")
        
        try:
            result = self.sdl1_ops.sdl1SolutionPreparation(params)
            logger.info(f"Solution preparation completed: {result.get('status')}")
            return result
        except Exception as e:
            logger.error(f"Solution preparation failed: {str(e)}")
            raise
    
    @task(name="SDL1 Electrode Setup", retries=2, retry_delay_seconds=20)
    def electrode_setup_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Prefect task for electrode setup"""
        logger = get_run_logger()
        logger.info(f"Setting up electrode: {params.get('electrode_type', 'Unknown')}")
        
        try:
            result = self.sdl1_ops.sdl1ElectrodeSetup(params)
            logger.info(f"Electrode setup completed: {result.get('status')}")
            return result
        except Exception as e:
            logger.error(f"Electrode setup failed: {str(e)}")
            raise
    
    @task(name="SDL1 Electrochemical Measurement", retries=1, retry_delay_seconds=60)
    def electrochemical_measurement_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Prefect task for electrochemical measurements"""
        logger = get_run_logger()
        measurement_type = params.get('measurement_type', 'Unknown')
        logger.info(f"Starting electrochemical measurement: {measurement_type}")
        
        try:
            result = self.sdl1_ops.sdl1ElectrochemicalMeasurement(params)
            logger.info(f"Measurement completed: {result.get('status')}")
            return result
        except Exception as e:
            logger.error(f"Electrochemical measurement failed: {str(e)}")
            raise
    
    @task(name="SDL1 Wash Cleaning", retries=2, retry_delay_seconds=30)
    def wash_cleaning_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Prefect task for wash/cleaning operations"""
        logger = get_run_logger()
        cycles = params.get('cleaning_cycles', 1)
        logger.info(f"Starting cleaning: {cycles} cycles")
        
        try:
            result = self.sdl1_ops.sdl1WashCleaning(params)
            logger.info(f"Cleaning completed: {result.get('status')}")
            return result
        except Exception as e:
            logger.error(f"Cleaning failed: {str(e)}")
            raise
    
    @task(name="SDL1 Data Export", retries=3, retry_delay_seconds=10)
    def data_export_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Prefect task for data export"""
        logger = get_run_logger()
        export_format = params.get('export_format', 'CSV')
        logger.info(f"Exporting data in {export_format} format")
        
        try:
            result = self.sdl1_ops.sdl1DataExport(params)
            logger.info(f"Data export completed: {result.get('status')}")
            return result
        except Exception as e:
            logger.error(f"Data export failed: {str(e)}")
            raise
    
    @task(name="SDL1 Sequence Control", retries=1, retry_delay_seconds=5)
    def sequence_control_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Prefect task for sequence control"""
        logger = get_run_logger()
        loop_count = params.get('loop_count', 1)
        logger.info(f"Configuring sequence control: {loop_count} loops")

        try:
            result = self.sdl1_ops.sdl1SequenceControl(params)
            logger.info(f"Sequence control completed: {result.get('status')}")
            return result
        except Exception as e:
            logger.error(f"Sequence control failed: {str(e)}")
            raise

    @task(name="SDL1 Sample Preparation", retries=2, retry_delay_seconds=10)
    def sample_preparation_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Prefect task for sample preparation with additives"""
        logger = get_run_logger()
        target_cell = params.get('target_cell', 'A1')
        total_volume = params.get('total_volume', 3000)
        logger.info(f"Starting sample preparation: {total_volume}μL in cell {target_cell}")

        try:
            result = self.sdl1_ops.sdl1SamplePreparation(params)
            logger.info(f"Sample preparation completed: {result.get('status')}")
            return result
        except Exception as e:
            logger.error(f"Sample preparation failed: {str(e)}")
            raise

    @task(name="SDL1 Electrode Manipulation", retries=2, retry_delay_seconds=10)
    def electrode_manipulation_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Prefect task for electrode manipulation operations"""
        logger = get_run_logger()
        operation_type = params.get('operation_type', 'pickup')
        electrode_type = params.get('electrode_type', 'reference')
        logger.info(f"Starting electrode manipulation: {operation_type} {electrode_type}")

        try:
            result = self.sdl1_ops.sdl1ElectrodeManipulation(params)
            logger.info(f"Electrode manipulation completed: {result.get('status')}")
            return result
        except Exception as e:
            logger.error(f"Electrode manipulation failed: {str(e)}")
            raise

    @task(name="SDL1 Hardware Washing", retries=1, retry_delay_seconds=15)
    def hardware_washing_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Prefect task for hardware washing with Arduino control"""
        logger = get_run_logger()
        target_cell = params.get('target_cell', 'A1')
        ultrasonic_duration = params.get('ultrasonic_duration', 5000)
        logger.info(f"Starting hardware washing: cell {target_cell}, ultrasonic {ultrasonic_duration}ms")

        try:
            result = self.sdl1_ops.sdl1HardwareWashing(params)
            logger.info(f"Hardware washing completed: {result.get('status')}")
            return result
        except Exception as e:
            logger.error(f"Hardware washing failed: {str(e)}")
            raise
    
    @task(name="SDL1 Cycle Counter", retries=1, retry_delay_seconds=5)
    def cycle_counter_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Prefect task for cycle counting"""
        logger = get_run_logger()
        current_cycle = params.get('current_cycle', 1)
        total_cycles = params.get('total_cycles', 1)
        logger.info(f"Cycle counter: {current_cycle}/{total_cycles}")
        
        try:
            result = self.sdl1_ops.sdl1CycleCounter(params)
            logger.info(f"Cycle counter completed: {result.get('status')}")
            return result
        except Exception as e:
            logger.error(f"Cycle counter failed: {str(e)}")
            raise
    
    def get_task_function(self, operation_type: str):
        """Get the appropriate Prefect task function for an operation type"""
        task_map = {
            "sdl1ExperimentSetup": self.experiment_setup_task,
            "sdl1SolutionPreparation": self.solution_preparation_task,
            "sdl1SamplePreparation": self.sample_preparation_task,  # New operation
            "sdl1ElectrodeSetup": self.electrode_setup_task,
            "sdl1ElectrodeManipulation": self.electrode_manipulation_task,  # New operation
            "sdl1ElectrochemicalMeasurement": self.electrochemical_measurement_task,
            "sdl1WashCleaning": self.wash_cleaning_task,
            "sdl1HardwareWashing": self.hardware_washing_task,  # New operation
            "sdl1DataExport": self.data_export_task,
            "sdl1SequenceControl": self.sequence_control_task,
            "sdl1CycleCounter": self.cycle_counter_task
        }
        return task_map.get(operation_type)
    
    @flow(name="SDL1 Canvas Workflow", 
          task_runner=SequentialTaskRunner(),
          retries=1,
          retry_delay_seconds=60)
    def execute_canvas_workflow_flow(self, canvas_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prefect flow for executing Canvas workflows
        
        Args:
            canvas_json: Canvas workflow JSON structure
            
        Returns:
            Workflow execution results
        """
        logger = get_run_logger()
        
        # Extract workflow metadata
        metadata = canvas_json.get("metadata", {})
        workflow_data = canvas_json.get("workflow", {})
        nodes = workflow_data.get("nodes", [])
        
        workflow_name = metadata.get("name", "Unnamed Workflow")
        workflow_id = metadata.get("id", "unknown")
        
        logger.info(f"Starting Canvas workflow: {workflow_name} ({workflow_id})")
        logger.info(f"Total nodes: {len(nodes)}")
        
        # Clear previous experiment data
        self.sdl1_ops.clear_experiment_data()
        
        # Execute nodes sequentially
        results = []
        failed_nodes = []
        
        for i, node in enumerate(nodes):
            node_type = node.get("type")
            node_id = node.get("id", f"node_{i}")
            node_params = node.get("params", {})
            
            logger.info(f"Executing node {i+1}/{len(nodes)}: {node_type} ({node_id})")
            
            # Get the appropriate task function
            task_func = self.get_task_function(node_type)
            
            if not task_func:
                error_msg = f"Unknown operation type: {node_type}"
                logger.error(error_msg)
                failed_nodes.append(node_id)
                results.append({
                    "node_id": node_id,
                    "node_type": node_type,
                    "status": "error",
                    "message": error_msg
                })
                continue
            
            try:
                # Execute the task
                result = task_func(node_params)
                result["node_id"] = node_id
                result["node_type"] = node_type
                results.append(result)
                
                if result.get("status") == "error":
                    failed_nodes.append(node_id)
                    
            except Exception as e:
                error_msg = f"Task execution failed: {str(e)}"
                logger.error(error_msg)
                failed_nodes.append(node_id)
                results.append({
                    "node_id": node_id,
                    "node_type": node_type,
                    "status": "error",
                    "message": error_msg,
                    "exception": str(e)
                })
        
        # Compile final results
        execution_status = "success" if not failed_nodes else "partial_failure" if len(failed_nodes) < len(nodes) else "failure"
        
        final_result = {
            "status": execution_status,
            "workflow_name": workflow_name,
            "workflow_id": workflow_id,
            "executed_nodes": len(results),
            "successful_nodes": len(nodes) - len(failed_nodes),
            "failed_nodes": failed_nodes,
            "results": results,
            "canvas_metadata": metadata,
            "execution_timestamp": datetime.now().isoformat(),
            "sdl1_operation_log": self.sdl1_ops.get_operation_log()
        }
        
        logger.info(f"Workflow execution completed: {execution_status}")
        logger.info(f"Successful nodes: {final_result['successful_nodes']}/{len(nodes)}")
        
        return final_result
