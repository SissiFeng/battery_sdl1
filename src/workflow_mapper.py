"""
JSON-to-Function Mapping System
Maps Canvas JSON workflow nodes to Opentrons function calls
Updated for Canvas SDL1 format
"""

import logging
from typing import Dict, List, Any, Optional, Callable
from opentrons_functions import OpentronsController
from sdl1_operations import SDL1Operations


class WorkflowMapper:
    """
    Maps JSON workflow nodes to Opentrons function calls
    Handles parameter conversion and validation
    """
    
    def __init__(self, controller: OpentronsController):
        self.controller = controller
        self.sdl1_ops = SDL1Operations(controller)
        self.function_map = self._build_function_map()
        self.execution_log = []
    
    def _build_function_map(self) -> Dict[str, Callable]:
        """Build mapping from JSON node types to controller functions"""
        return {
            # Basic Opentrons operations (backward compatibility)
            "initialize_robot": self.controller.initialize_robot,
            "load_labware": self._load_labware_wrapper,
            "load_custom_labware": self._load_custom_labware_wrapper,
            "load_pipette": self._load_pipette_wrapper,
            "home_robot": self.controller.home_robot,
            "set_lights": self._set_lights_wrapper,
            "move_to_well": self._move_to_well_wrapper,
            "aspirate": self._aspirate_wrapper,
            "dispense": self._dispense_wrapper,
            "blowout": self._blowout_wrapper,
            "fill_well": self._fill_well_wrapper,
            "pickup_tip": self._pickup_tip_wrapper,
            "drop_tip": self._drop_tip_wrapper,
            "delay": self._delay_wrapper,
            "get_status": self.controller.get_status,
            "get_labware_registry": self.controller.get_labware_registry,
            
            # SDL1 Unit Operations (Canvas format)
            "sdl1ExperimentSetup": self.sdl1_ops.sdl1ExperimentSetup,
            "sdl1SolutionPreparation": self.sdl1_ops.sdl1SolutionPreparation,
            "sdl1SamplePreparation": self.sdl1_ops.sdl1SamplePreparation,  # New operation
            "sdl1ElectrodeSetup": self.sdl1_ops.sdl1ElectrodeSetup,
            "sdl1ElectrodeManipulation": self.sdl1_ops.sdl1ElectrodeManipulation,  # New operation
            "sdl1ElectrochemicalMeasurement": self.sdl1_ops.sdl1ElectrochemicalMeasurement,
            "sdl1WashCleaning": self.sdl1_ops.sdl1WashCleaning,
            "sdl1HardwareWashing": self.sdl1_ops.sdl1HardwareWashing,  # New operation
            "sdl1DataExport": self.sdl1_ops.sdl1DataExport,
            "sdl1SequenceControl": self.sdl1_ops.sdl1SequenceControl,
            "sdl1CycleCounter": self.sdl1_ops.sdl1CycleCounter
        }
    
    def convert_params(self, node_params: Dict[str, Any], expected_params: List[str]) -> Dict[str, Any]:
        """
        Convert JSON parameters to function parameters
        Handles parameter name mapping and type conversion
        """
        param_mapping = {
            # Common mappings
            "labware": "labware_name",
            "well": "well_name", 
            "pipette": "pipette_name",
            "slot": "slot",
            "volume": "volume",
            "speed": "speed",
            "seconds": "seconds",
            "message": "message",
            "on": "on",
            "mount": "mount",
            
            # Offset mappings
            "offset_start": "offset_start",
            "offset_x": "offset_x",
            "offset_y": "offset_y", 
            "offset_z": "offset_z",
            "offset_start_from": "offset_start_from",
            "offset_start_to": "offset_start_to",
            "offset_x_from": "offset_x_from",
            "offset_y_from": "offset_y_from",
            "offset_z_from": "offset_z_from",
            "offset_x_to": "offset_x_to",
            "offset_y_to": "offset_y_to",
            "offset_z_to": "offset_z_to",
            
            # Specific mappings
            "labware_name": "labware_name",
            "labware_file_path": "labware_file_path",
            "pipette_name": "pipette_name",
            "source_labware": "source_labware",
            "source_well": "source_well",
            "dest_labware": "dest_labware",
            "dest_well": "dest_well",
            "move_speed": "move_speed",
            "drop_in_disposal": "drop_in_disposal"
        }
        
        converted = {}
        for param in expected_params:
            # Try direct mapping first
            if param in node_params:
                converted[param] = node_params[param]
            # Try mapped name
            elif param in param_mapping.values():
                reverse_key = next(k for k, v in param_mapping.items() if v == param)
                if reverse_key in node_params:
                    converted[param] = node_params[reverse_key]
            # Set defaults for common parameters
            elif param in ["offset_x", "offset_y", "offset_z"]:
                converted[param] = node_params.get(param, 0.0)
            elif param == "offset_start":
                converted[param] = node_params.get(param, "top")
            elif param == "speed":
                converted[param] = node_params.get(param, 100)
            elif param == "drop_in_disposal":
                converted[param] = node_params.get(param, True)
        
        return converted
    
    # Wrapper functions to handle parameter conversion
    def _load_labware_wrapper(self, params: Dict[str, Any]) -> Dict[str, Any]:
        converted = self.convert_params(params, ["slot", "labware_name", "labware_id"])
        return self.controller.load_labware(**converted)
    
    def _load_custom_labware_wrapper(self, params: Dict[str, Any]) -> Dict[str, Any]:
        converted = self.convert_params(params, ["slot", "labware_file_path"])
        return self.controller.load_custom_labware(**converted)
    
    def _load_pipette_wrapper(self, params: Dict[str, Any]) -> Dict[str, Any]:
        converted = self.convert_params(params, ["pipette_name", "mount"])
        return self.controller.load_pipette(**converted)
    
    def _set_lights_wrapper(self, params: Dict[str, Any]) -> Dict[str, Any]:
        converted = self.convert_params(params, ["on"])
        return self.controller.set_lights(**converted)
    
    def _move_to_well_wrapper(self, params: Dict[str, Any]) -> Dict[str, Any]:
        expected = ["labware_name", "well_name", "pipette_name", "offset_start", 
                   "offset_x", "offset_y", "offset_z", "speed"]
        converted = self.convert_params(params, expected)
        return self.controller.move_to_well(**converted)
    
    def _aspirate_wrapper(self, params: Dict[str, Any]) -> Dict[str, Any]:
        expected = ["labware_name", "well_name", "pipette_name", "volume", 
                   "offset_start", "offset_x", "offset_y", "offset_z"]
        converted = self.convert_params(params, expected)
        return self.controller.aspirate(**converted)
    
    def _dispense_wrapper(self, params: Dict[str, Any]) -> Dict[str, Any]:
        expected = ["labware_name", "well_name", "pipette_name", "volume",
                   "offset_start", "offset_x", "offset_y", "offset_z"]
        converted = self.convert_params(params, expected)
        return self.controller.dispense(**converted)
    
    def _blowout_wrapper(self, params: Dict[str, Any]) -> Dict[str, Any]:
        expected = ["labware_name", "well_name", "pipette_name", "offset_start",
                   "offset_x", "offset_y", "offset_z"]
        converted = self.convert_params(params, expected)
        return self.controller.blowout(**converted)
    
    def _fill_well_wrapper(self, params: Dict[str, Any]) -> Dict[str, Any]:
        expected = ["source_labware", "source_well", "dest_labware", "dest_well",
                   "pipette_name", "volume", "offset_start_from", "offset_start_to",
                   "offset_x_from", "offset_y_from", "offset_z_from",
                   "offset_x_to", "offset_y_to", "offset_z_to", "move_speed"]
        converted = self.convert_params(params, expected)
        return self.controller.fill_well(**converted)
    
    def _pickup_tip_wrapper(self, params: Dict[str, Any]) -> Dict[str, Any]:
        expected = ["labware_name", "well_name", "pipette_name", "offset_x", "offset_y"]
        converted = self.convert_params(params, expected)
        return self.controller.pickup_tip(**converted)
    
    def _drop_tip_wrapper(self, params: Dict[str, Any]) -> Dict[str, Any]:
        expected = ["labware_name", "well_name", "pipette_name", "offset_start",
                   "offset_x", "offset_y", "offset_z", "drop_in_disposal"]
        converted = self.convert_params(params, expected)
        return self.controller.drop_tip(**converted)
    
    def _delay_wrapper(self, params: Dict[str, Any]) -> Dict[str, Any]:
        expected = ["seconds", "message"]
        converted = self.convert_params(params, expected)
        return self.controller.delay(**converted)
    
    def execute_node(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single workflow node
        
        Args:
            node: JSON node with 'type' and 'params' fields
            
        Returns:
            Execution result dictionary
        """
        node_type = node.get("type")
        node_params = node.get("params", {})
        node_id = node.get("id", "unknown")
        
        if node_type not in self.function_map:
            error_msg = f"Unknown node type: {node_type}"
            logging.error(error_msg)
            return {"status": "error", "message": error_msg, "node_id": node_id}
        
        try:
            # Log the execution
            self.execution_log.append({
                "node_id": node_id,
                "node_type": node_type,
                "params": node_params,
                "timestamp": logging.time.time() if hasattr(logging, 'time') else 0
            })
            
            # Execute the function
            function = self.function_map[node_type]
            
            # Handle functions that don't need parameters
            if node_type in ["initialize_robot", "home_robot", "get_status", "get_labware_registry"]:
                result = function()
            else:  
                # For SDL1 operations, pass the full params dict
                # For basic operations, use wrapper functions for parameter conversion
                if node_type.startswith("sdl1"):
                    result = function(node_params)
                else:
                    result = function(node_params)
            
            # Add node tracking info to result
            result["node_id"] = node_id
            result["node_type"] = node_type
            
            logging.info(f"Successfully executed {node_type} ({node_id}): {result.get('status', 'unknown')}")
            return result
            
        except Exception as e:
            error_msg = f"Error executing {node_type} ({node_id}): {str(e)}"
            logging.error(error_msg)
            return {
                "status": "error", 
                "message": error_msg, 
                "exception": str(e),
                "node_id": node_id,
                "node_type": node_type
            }
    
    def execute_canvas_workflow(self, canvas_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute Canvas workflow from full JSON structure
        
        Args:
            canvas_json: Full Canvas JSON with metadata and workflow structure
            
        Returns:
            Overall execution result
        """
        # Extract workflow nodes from Canvas structure
        workflow_data = canvas_json.get("workflow", {})
        nodes = workflow_data.get("nodes", [])
        metadata = canvas_json.get("metadata", {})
        
        logging.info(f"Starting Canvas workflow: {metadata.get('name', 'Unnamed')} - {len(nodes)} nodes")
        
        # Clear previous experiment data
        self.sdl1_ops.clear_experiment_data()
        
        # Execute workflow
        result = self.execute_workflow(nodes)
        
        # Add Canvas-specific metadata to result
        result["canvas_metadata"] = metadata
        result["workflow_name"] = metadata.get("name", "Unnamed")
        result["workflow_id"] = metadata.get("id", "unknown")
        
        return result
    
    def execute_workflow(self, workflow: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute complete workflow from JSON
        
        Args:
            workflow: List of JSON nodes
            
        Returns:
            Overall execution result
        """
        results = []
        failed_nodes = []
        
        logging.info(f"Starting workflow execution with {len(workflow)} nodes")
        
        for i, node in enumerate(workflow):
            node_type = node.get('type', 'unknown')
            node_id = node.get('id', f'node_{i}')
            
            logging.info(f"Executing node {i+1}/{len(workflow)}: {node_type} ({node_id})")
            
            result = self.execute_node(node)
            results.append({
                "node_index": i,
                "node_id": node_id,
                "node_type": node_type,
                "result": result
            })
            
            # Check if execution failed
            if result.get("status") == "error":
                failed_nodes.append({
                    "index": i,
                    "node_id": node_id,
                    "node_type": node_type,
                    "error": result.get("message", "Unknown error")
                })
                
                # Check error handling strategy
                error_handling = node.get("params", {}).get("error_handling", "continue")
                if error_handling == "stop":
                    logging.error(f"Node {node_id} failed with stop policy - halting workflow")
                    break
                else:
                    logging.warning(f"Node {node_id} failed but continuing workflow")
        
        # Workflow summary
        summary = {
            "status": "completed" if not failed_nodes else "completed_with_errors",
            "total_nodes": len(workflow),
            "executed_nodes": len(results),
            "successful_nodes": len(workflow) - len(failed_nodes),
            "failed_nodes": failed_nodes,
            "results": results,
            "execution_log": self.execution_log,
            "sdl1_operation_log": self.sdl1_ops.get_operation_log()
        }
        
        logging.info(f"Workflow execution completed. Status: {summary['status']}")
        return summary
    
    def validate_workflow(self, workflow: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate workflow without executing
        
        Args:
            workflow: List of JSON nodes
            
        Returns:
            Validation result
        """
        validation_errors = []
        
        for i, node in enumerate(workflow):
            node_type = node.get("type")
            
            # Check if node type is supported
            if not node_type:
                validation_errors.append(f"Node {i}: Missing 'type' field")
                continue
                
            if node_type not in self.function_map:
                validation_errors.append(f"Node {i}: Unknown type '{node_type}'")
                continue
            
            # Basic parameter validation
            params = node.get("params", {})
            if not isinstance(params, dict):
                validation_errors.append(f"Node {i}: 'params' must be a dictionary")
        
        return {
            "valid": len(validation_errors) == 0,
            "errors": validation_errors,
            "total_nodes": len(workflow)
        }
    
    def get_supported_operations(self) -> List[str]:
        """Get list of all supported operation types"""
        return list(self.function_map.keys())
    
    def clear_execution_log(self):
        """Clear the execution log"""
        self.execution_log = []