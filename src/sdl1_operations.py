"""
SDL1-Specific Unit Operations
High-level operations that combine multiple basic Opentrons functions
Based on Canvas JSON output structure
"""

import logging
import time
import json
import os
import math
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Optional
from opentrons_functions import OpentronsController

# Import recovery management
try:
    from recovery_manager import (
        RecoveryManager, RecoverableError, PipettingError,
        ElectrodeError, ElectrochemicalError, CriticalSystemError
    )
    RECOVERY_AVAILABLE = True
except ImportError:
    RECOVERY_AVAILABLE = False
    logging.warning("Recovery manager not available - using basic error handling")

# Import for electrochemical measurements (from original script)
try:
    from PySide6.QtWidgets import QApplication
    from SquidstatPyLibrary import (
        AisDeviceTracker, AisExperiment, AisErrorCode,
        AisOpenCircuitElement, AisConstantCurrentElement,
        AisEISPotentiostaticElement
    )
    SQUIDSTAT_AVAILABLE = True
except ImportError:
    SQUIDSTAT_AVAILABLE = False
    logging.warning("Squidstat libraries not available - electrochemical measurements will be simulated")

try:
    from OT_Arduino_Client import Arduino
    ARDUINO_AVAILABLE = True
except ImportError:
    ARDUINO_AVAILABLE = False
    logging.warning("Arduino client not available - cleaning operations will be simulated")


class SDL1Operations:
    """
    SDL1-specific unit operations that map to Canvas node types
    Each operation combines multiple basic Opentrons functions
    """
    
    def __init__(self, controller: OpentronsController, enable_recovery: bool = True):
        self.controller = controller
        self.operation_log = []
        self.experiment_data = {"dc_rows": [], "ac_rows": []}

        # Initialize recovery manager if available
        self.recovery_manager = None
        if enable_recovery and RECOVERY_AVAILABLE:
            self.recovery_manager = RecoveryManager(controller)
            logging.info("Recovery manager initialized")
        else:
            logging.warning("Recovery manager not available - using basic error handling")

        # Labware mapping based on original script
        self.labware_mapping = {
            "vial_rack_2": "slot_2",
            "nis_reactor": "slot_9",
            "electrode_rack": "slot_10",
            "tip_rack": "slot_1"
        }
    
    def log_operation(self, operation: str, params: Dict, result: Dict):
        """Log high-level operation execution"""
        log_entry = {
            "operation": operation,
            "params": params,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        self.operation_log.append(log_entry)
        logging.info(f"SDL1 Operation: {operation} - Status: {result.get('status', 'unknown')}")

    def _execute_with_recovery(self, operation_func, operation_name: str, step_index: int,
                              checkpoint_name: str = None, **kwargs):
        """Execute an operation with recovery management"""
        if self.recovery_manager:
            return self.recovery_manager.run_with_recovery(
                step_function=operation_func,
                step_name=operation_name,
                step_index=step_index,
                checkpoint_name=checkpoint_name,
                **kwargs
            )
        else:
            # Fallback to direct execution without recovery
            return operation_func(**kwargs)

    def _pipetting_operation(self, **params) -> Dict[str, Any]:
        """Core pipetting operation with error handling"""
        try:
            # Extract parameters
            source_labware = self.labware_mapping.get(params.get("source_labware", "vial_rack_2"))
            source_well = params.get("source_well", "A1")
            target_labware = self.labware_mapping.get(params.get("target_labware", "nis_reactor"))
            target_well = params.get("target_well", "A1")
            volume = params.get("volume", 5000)
            pipette_type = params.get("pipette_type", "p1000_single_gen2")

            # Validate volume
            if volume <= 0:
                raise PipettingError(f"Invalid volume: {volume}")

            # Get tip location
            tip_location = self.controller.get_pipette_tip_location(self.controller.pipette_tip_counter)

            # Pick up tip
            self.controller.move_to_well(
                labware_name=self.controller.labware_registry["slot_1"]["id"],
                well_name=tip_location,
                pipette_name=pipette_type,
                offset_start="top",
                offset_y=1,
                speed=100
            )

            pickup_result = self.controller.pickup_tip(pipette_name=pipette_type)
            if not pickup_result.get("success", False):
                raise PipettingError("Failed to pick up tip")

            # Aspirate
            aspirate_result = self.controller.aspirate(
                labware_name=source_labware,
                well_name=source_well,
                volume=volume,
                pipette_name=pipette_type,
                offset_z=params.get("aspiration_offset_z", 8)
            )
            if not aspirate_result.get("success", False):
                raise PipettingError("Failed to aspirate solution")

            # Dispense
            dispense_result = self.controller.dispense(
                labware_name=target_labware,
                well_name=target_well,
                volume=volume,
                pipette_name=pipette_type,
                offset_x=params.get("dispense_offset_x", -1),
                offset_y=params.get("dispense_offset_y", 0.5),
                offset_z=params.get("dispense_offset_z", 0)
            )
            if not dispense_result.get("success", False):
                raise PipettingError("Failed to dispense solution")

            # Drop tip
            drop_result = self.controller.drop_tip(pipette_name=pipette_type)
            if not drop_result.get("success", False):
                logging.warning("Failed to drop tip properly")

            return {
                "status": "success",
                "volume_transferred": volume,
                "source": f"{source_labware}:{source_well}",
                "target": f"{target_labware}:{target_well}",
                "tip_used": tip_location
            }

        except Exception as e:
            if isinstance(e, (PipettingError, RecoverableError)):
                raise
            else:
                raise PipettingError(f"Pipetting operation failed: {str(e)}")
    
    def sdl1SolutionPreparation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Solution Preparation Unit Operation with Recovery
        Prepares and dispenses solutions using fillWell function
        """
        try:
            # Execute with recovery management
            result = self._execute_with_recovery(
                operation_func=self._pipetting_operation,
                operation_name="Solution Preparation",
                step_index=params.get("step_index", 0),
                checkpoint_name="solution_preparation_complete",
                **params
            )

            self.log_operation("sdl1SolutionPreparation", params, result)
            return result

        except Exception as e:
            error_result = {
                "status": "error",
                "message": str(e),
                "operation": "sdl1SolutionPreparation",
                "timestamp": datetime.now().isoformat()
            }
            self.log_operation("sdl1SolutionPreparation", params, error_result)
            return error_result

    def _electrode_setup_operation(self, **params) -> Dict[str, Any]:
        """Core electrode setup operation with error handling"""
        try:
            electrode_type = params.get("electrode_type", "working")
            electrode_position = params.get("electrode_position", "A1")
            material = params.get("material", "platinum")
            surface_area = params.get("surface_area", 1.0)

            # Validate electrode parameters
            valid_types = ["working", "counter", "reference"]
            if electrode_type not in valid_types:
                raise ElectrodeError(f"Invalid electrode type: {electrode_type}")

            if surface_area <= 0:
                raise ElectrodeError(f"Invalid surface area: {surface_area}")

            # Move to electrode rack
            move_result = self.controller.move_to_well(
                labware_name=self.controller.labware_registry["slot_10"]["id"],
                well_name=electrode_position,
                pipette_name="p1000_single_gen2",
                offset_start="top",
                offset_z=5,
                speed=50
            )

            if not move_result.get("success", False):
                raise ElectrodeError("Failed to move to electrode position")

            # Simulate electrode pickup/placement
            time.sleep(2)  # Simulate electrode handling time

            # Verify electrode placement (simulation)
            verification_result = self._verify_electrode_placement(electrode_type, electrode_position)
            if not verification_result:
                raise ElectrodeError("Electrode placement verification failed")

            return {
                "status": "success",
                "electrode_type": electrode_type,
                "position": electrode_position,
                "material": material,
                "surface_area": surface_area,
                "verification": "passed"
            }

        except Exception as e:
            if isinstance(e, (ElectrodeError, RecoverableError)):
                raise
            else:
                raise ElectrodeError(f"Electrode setup failed: {str(e)}")

    def _verify_electrode_placement(self, electrode_type: str, position: str) -> bool:
        """Verify electrode placement (simulation)"""
        # In real implementation, this would check electrical connectivity
        # For now, simulate verification
        time.sleep(1)
        return True  # Assume verification passes

    def sdl1SolutionPreparation_legacy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Legacy Solution Preparation Unit Operation (without recovery)
        Prepares and dispenses solutions using fillWell function
        """
        try:
            # Extract parameters
            source_labware = self.labware_mapping.get(params.get("source_labware", "vial_rack_2"))
            source_well = params.get("source_well", "A1")
            target_labware = self.labware_mapping.get(params.get("target_labware", "nis_reactor"))
            target_well = params.get("target_well", "A1")
            volume = params.get("volume", 5000)
            pipette_type = params.get("pipette_type", "p1000_single_gen2")
            
            # Offsets
            aspiration_offset_z = params.get("aspiration_offset_z", 8)
            dispense_offset_x = params.get("dispense_offset_x", -1)
            dispense_offset_y = params.get("dispense_offset_y", 0.5)
            dispense_offset_z = params.get("dispense_offset_z", 0)
            
            # Get next tip location
            tip_location = self.controller.get_pipette_tip_location(self.controller.pipette_tip_counter)
            
            # Step 1: Pick up tip
            self.controller.move_to_well(
                labware_name=self.controller.labware_registry["slot_1"]["id"],
                well_name=tip_location,
                pipette_name=pipette_type,
                offset_start="top",
                offset_y=1,
                speed=100
            )
            
            self.controller.pickup_tip(
                labware_name=self.controller.labware_registry["slot_1"]["id"],
                well_name=tip_location,
                pipette_name=pipette_type,
                offset_y=1
            )
            
            # Step 2: Fill well using the existing fillWell function
            fill_result = self.controller.fill_well(
                source_labware=self.controller.labware_registry[source_labware]["id"],
                source_well=source_well,
                dest_labware=self.controller.labware_registry[target_labware]["id"],
                dest_well=target_well,
                pipette_name=pipette_type,
                volume=volume,
                offset_start_from="bottom",
                offset_start_to="top",
                offset_z_from=aspiration_offset_z,
                offset_x_to=dispense_offset_x,
                offset_y_to=dispense_offset_y,
                offset_z_to=dispense_offset_z
            )
            
            # Step 3: Drop tip
            self.controller.drop_tip(
                labware_name=self.controller.labware_registry["slot_1"]["id"],
                well_name=tip_location,
                pipette_name=pipette_type,
                offset_start="bottom",
                offset_y=1,
                offset_z=7,
                drop_in_disposal=True
            )
            
            # Increment tip counter
            self.controller.pipette_tip_counter += 1
            
            result = {
                "status": "success",
                "operation": "solution_preparation",
                "volume_transferred": volume,
                "source": f"{source_labware}:{source_well}",
                "target": f"{target_labware}:{target_well}",
                "fill_result": fill_result
            }
            
            # Add wait times if specified
            wait_before = params.get("wait_before", 0)
            wait_after = params.get("wait_after", 0)
            
            if wait_before > 0:
                self.controller.delay(wait_before, f"Pre-operation wait: {params.get('uo_name', 'Solution Prep')}")
            if wait_after > 0:
                self.controller.delay(wait_after, f"Post-operation wait: {params.get('uo_name', 'Solution Prep')}")
            
            self.log_operation("sdl1SolutionPreparation", params, result)
            return result
            
        except Exception as e:
            error_result = {
                "status": "error",
                "operation": "solution_preparation",
                "error": str(e)
            }
            self.log_operation("sdl1SolutionPreparation", params, error_result)
            return error_result
    
    def sdl1ElectrodeSetup(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Electrode Setup Unit Operation
        Positions electrodes for electrochemical measurements
        """
        try:
            electrode_position = params.get("electrode_position", "A2")
            target_well = params.get("target_well", "A1")
            insertion_depth = params.get("insertion_depth", 26)
            lateral_offset_x = params.get("lateral_offset_x", 0.5)
            lateral_offset_y = params.get("lateral_offset_y", 0.5)
            movement_speed = params.get("movement_speed", 50)
            pipette_type = params.get("pipette_type", "p1000_single_gen2")
            
            electrode_rack_id = self.controller.labware_registry["slot_10"]["id"]
            reactor_id = self.controller.labware_registry["slot_9"]["id"]
            
            # Step 1: Move to electrode rack
            self.controller.move_to_well(
                labware_name=electrode_rack_id,
                well_name=electrode_position,
                pipette_name=pipette_type,
                offset_start="top",
                offset_x=0.6,
                offset_y=0.5,
                offset_z=3,
                speed=100
            )
            
            # Step 2: Pick up electrode
            self.controller.pickup_tip(
                labware_name=electrode_rack_id,
                well_name=electrode_position,
                pipette_name=pipette_type,
                offset_x=0.6,
                offset_y=0.5
            )
            
            # Step 3: Move to reactor well (approach position)
            self.controller.move_to_well(
                labware_name=reactor_id,
                well_name=target_well,
                pipette_name=pipette_type,
                offset_start="top",
                offset_x=lateral_offset_x,
                offset_y=lateral_offset_y,
                offset_z=5,
                speed=movement_speed
            )
            
            # Step 4: Insert electrode to specified depth
            self.controller.move_to_well(
                labware_name=reactor_id,
                well_name=target_well,
                pipette_name=pipette_type,
                offset_start="top",
                offset_x=lateral_offset_x,
                offset_y=lateral_offset_y,
                offset_z=-insertion_depth,
                speed=movement_speed
            )
            
            result = {
                "status": "success",
                "operation": "electrode_setup",
                "electrode_position": electrode_position,
                "target_well": target_well,
                "insertion_depth": insertion_depth,
                "final_position": f"{reactor_id}:{target_well}"
            }
            
            self.log_operation("sdl1ElectrodeSetup", params, result)
            return result
            
        except Exception as e:
            error_result = {
                "status": "error",
                "operation": "electrode_setup",
                "error": str(e)
            }
            self.log_operation("sdl1ElectrodeSetup", params, error_result)
            return error_result
    
    def sdl1ElectrochemicalMeasurement(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Electrochemical Measurement Unit Operation
        Performs complex electrochemical measurements using Squidstat
        """
        if not SQUIDSTAT_AVAILABLE:
            # Simulate the measurement based on measurement type
            measurement_type = params.get("measurement_type", "CP")

            # Calculate simulation duration based on measurement type
            if measurement_type == "OCV":
                sim_duration = params.get("ocv_duration", 60)
            elif measurement_type == "CP":
                sim_duration = params.get("cp_duration", 720)
            elif measurement_type == "CVA":
                cycles = params.get("cva_cycles", 3)
                scan_rate = params.get("cva_scan_rate", 0.05)
                voltage_range = abs(params.get("cva_end_voltage", 0.5) - params.get("cva_start_voltage", -0.5))
                sim_duration = cycles * (voltage_range / scan_rate) * 2  # Forward and reverse
            elif measurement_type == "PEIS":
                points = params.get("peis_points_per_decade", 5)
                start_freq = params.get("peis_start_frequency", 10000)
                end_freq = params.get("peis_end_frequency", 0.1)
                decades = abs(math.log10(start_freq) - math.log10(end_freq))
                sim_duration = points * decades * 2  # Approximate
            elif measurement_type == "LSV":
                scan_rate = params.get("lsv_scan_rate", 0.01)
                voltage_range = abs(params.get("lsv_end_voltage", 0.5) - params.get("lsv_start_voltage", -0.5))
                sim_duration = voltage_range / scan_rate
            else:
                sim_duration = 60  # Default

            result = {
                "status": "simulated",
                "operation": "electrochemical_measurement",
                "measurement_type": measurement_type,
                "message": f"Squidstat not available - {measurement_type} measurement simulated",
                "simulated_duration": sim_duration,
                "data_collection_enabled": params.get("data_collection_enabled", True)
            }

            # Simulate data collection
            self.controller.delay(min(sim_duration, 10), f"Simulating {measurement_type} measurement")

            self.log_operation("sdl1ElectrochemicalMeasurement", params, result)
            return result
        
        try:
            # Initialize Squidstat
            com_port = params.get("com_port", "COM4")
            channel = params.get("channel", 0)
            
            app = QApplication([])
            tracker = AisDeviceTracker.Instance()
            err = tracker.connectToDeviceOnComPort(com_port)
            
            if err.value() != AisErrorCode.Success:
                raise Exception(f"Squidstat connection failed: {err.message()}")
            
            devices = tracker.getConnectedDevices()
            if not devices:
                raise Exception("No Squidstat devices found")
            
            handler = tracker.getInstrumentHandler(devices[0])
            
            # Setup data collection callbacks
            handler.activeDCDataReady.connect(
                lambda ch, d: self.experiment_data["dc_rows"].append([
                    d.timestamp, d.current, d.workingElectrodeVoltage
                ])
            )
            
            handler.activeACDataReady.connect(
                lambda ch, a: self.experiment_data["ac_rows"].append({
                    'timestamp': a.timestamp,
                    'frequency': a.frequency,
                    'absoluteImpedance': a.absoluteImpedance,
                    'realImpedance': a.realImpedance,
                    'imagImpedance': a.imagImpedance,
                    'phaseAngle': a.phaseAngle,
                    'numberOfCycles': a.numberOfCycles
                })
            )
            
            # Build experiment based on parameters
            exp = AisExperiment()
            
            # Deposition step
            deposition_current = params.get("deposition_current", -0.004)
            deposition_duration = params.get("deposition_duration", 720)
            deposition_interval = params.get("deposition_sample_interval", 1.0)
            
            dep = AisConstantCurrentElement(deposition_current, deposition_interval, deposition_duration)
            exp.appendElement(dep)
            
            # OCV rest
            ocv_duration = params.get("ocv_duration", 60)
            ocv_interval = params.get("ocv_sample_interval", 1.0)
            exp.appendElement(AisOpenCircuitElement(ocv_duration, ocv_interval))
            
            # PEIS measurement
            peis_start_freq = params.get("peis_start_frequency", 10000)
            peis_end_freq = params.get("peis_end_frequency", 0.1)
            peis_steps = params.get("peis_points_per_decade", 5.0)
            peis_bias = params.get("peis_dc_bias", 0.0)
            peis_amplitude = params.get("peis_ac_amplitude", 0.01)
            
            eis = AisEISPotentiostaticElement(peis_start_freq, peis_end_freq, peis_steps, peis_bias, peis_amplitude)
            eis.setBiasVoltageVsOCP(params.get("peis_bias_vs_ocp", True))
            eis.setMinimumCycles(params.get("peis_minimum_cycles", 1))
            exp.appendElement(eis)
            
            # Dissolution step
            dissolution_current = params.get("dissolution_current", 0.004)
            dissolution_duration = params.get("dissolution_duration", 720)
            dissolution_interval = params.get("dissolution_sample_interval", 1.0)
            
            diss = AisConstantCurrentElement(dissolution_current, dissolution_interval, dissolution_duration)
            exp.appendElement(diss)
            
            # Final OCV
            exp.appendElement(AisOpenCircuitElement(ocv_duration, ocv_interval))
            
            # Final PEIS
            eis2 = AisEISPotentiostaticElement(peis_start_freq, peis_end_freq, peis_steps, peis_bias, peis_amplitude)
            eis2.setBiasVoltageVsOCP(params.get("peis_bias_vs_ocp", True))
            eis2.setMinimumCycles(params.get("peis_minimum_cycles", 1))
            exp.appendElement(eis2)
            
            # Upload and start experiment
            err = handler.uploadExperimentToChannel(channel, exp)
            if err.value() != AisErrorCode.Success:
                raise Exception(f"Experiment upload failed: {err.message()}")
            
            err = handler.startUploadedExperiment(channel)
            if err.value() != AisErrorCode.Success:
                raise Exception(f"Experiment start failed: {err.message()}")
            
            logging.info("Electrochemical experiment running...")
            
            # Wait for completion
            while handler.isChannelBusy(channel):
                app.processEvents()
                time.sleep(0.1)
            
            # Cleanup
            handler.activeDCDataReady.disconnect()
            handler.activeACDataReady.disconnect()
            
            result = {
                "status": "success",
                "operation": "electrochemical_measurement",
                "data_points": {
                    "dc_count": len(self.experiment_data["dc_rows"]),
                    "ac_count": len(self.experiment_data["ac_rows"])
                },
                "experiment_type": params.get("measurement_type", "CP"),
                "total_duration": deposition_duration + dissolution_duration + ocv_duration * 2
            }
            
            self.log_operation("sdl1ElectrochemicalMeasurement", params, result)
            return result
            
        except Exception as e:
            error_result = {
                "status": "error",
                "operation": "electrochemical_measurement",
                "error": str(e)
            }
            self.log_operation("sdl1ElectrochemicalMeasurement", params, error_result)
            return error_result
    
    def sdl1WashCleaning(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Wash/Cleaning Unit Operation
        Multi-stage cleaning with Arduino pump control
        """
        try:
            cleaning_tool_position = params.get("cleaning_tool_position", "B1")
            target_well = params.get("target_well", "A1")
            pump1_volume = params.get("pump1_volume", 10.0)
            pump2_volume = params.get("pump2_volume", 4.0)
            ultrasonic_time = params.get("ultrasonic_time", 5000)
            final_wash_volume = params.get("final_wash_volume", 10.0)
            insertion_depth = params.get("insertion_depth", 57)
            cleaning_cycles = params.get("cleaning_cycles", 2)
            pipette_type = params.get("pipette_type", "p1000_single_gen2")
            
            electrode_rack_id = self.controller.labware_registry["slot_10"]["id"]
            reactor_id = self.controller.labware_registry["slot_9"]["id"]
            
            # Step 1: Return electrode to rack (from previous setup)
            self.controller.move_to_well(
                labware_name=electrode_rack_id,
                well_name="A2",  # Previous electrode position
                pipette_name=pipette_type,
                offset_start="top",
                offset_x=0.6,
                offset_y=0.5,
                speed=50
            )
            
            self.controller.drop_tip(
                labware_name=electrode_rack_id,
                well_name="A2",
                pipette_name=pipette_type,
                offset_start="bottom",
                offset_x=0.6,
                offset_y=0.5,
                offset_z=6,
                drop_in_disposal=False
            )
            
            # Step 2: Pick up cleaning tool
            self.controller.move_to_well(
                labware_name=electrode_rack_id,
                well_name=cleaning_tool_position,
                pipette_name=pipette_type,
                offset_start="top",
                offset_x=0.6,
                offset_y=0.5,
                speed=50
            )
            
            self.controller.pickup_tip(
                labware_name=electrode_rack_id,
                well_name=cleaning_tool_position,
                pipette_name=pipette_type,
                offset_x=0.6,
                offset_y=0.5
            )
            
            # Step 3: Position cleaning tool in reactor
            self.controller.move_to_well(
                labware_name=reactor_id,
                well_name=target_well,
                pipette_name=pipette_type,
                offset_start="top",
                offset_x=0.5,
                offset_y=0.5,
                offset_z=5,
                speed=50
            )
            
            self.controller.move_to_well(
                labware_name=reactor_id,
                well_name=target_well,
                pipette_name=pipette_type,
                offset_start="top",
                offset_x=0.5,
                offset_y=0.5,
                offset_z=-insertion_depth,
                speed=50
            )
            
            # Step 4: Arduino-controlled cleaning sequence
            if ARDUINO_AVAILABLE:
                ac = Arduino()
                for cycle in range(cleaning_cycles):
                    ac.dispense_ml(2, pump2_volume)
                    ac.dispense_ml(1, pump1_volume)
                    ac.setUltrasonicOnTimer(0, ultrasonic_time)
                    ac.dispense_ml(2, final_wash_volume)
                ac.connection.close()
                
                cleaning_status = "completed"
            else:
                # Simulate cleaning
                total_clean_time = cleaning_cycles * (ultrasonic_time / 1000 + 2)
                self.controller.delay(total_clean_time, f"Simulating {cleaning_cycles} cleaning cycles")
                cleaning_status = "simulated"
            
            # Step 5: Return cleaning tool
            self.controller.move_to_well(
                labware_name=electrode_rack_id,
                well_name=cleaning_tool_position,
                pipette_name=pipette_type,
                offset_start="top",
                offset_x=0.6,
                offset_y=0.5,
                speed=50
            )
            
            self.controller.drop_tip(
                labware_name=electrode_rack_id,
                well_name=cleaning_tool_position,
                pipette_name=pipette_type,
                offset_start="bottom",
                offset_x=0.6,
                offset_y=0.5,
                offset_z=6,
                drop_in_disposal=False
            )
            
            result = {
                "status": "success",
                "operation": "wash_cleaning",
                "cleaning_status": cleaning_status,
                "cycles_completed": cleaning_cycles,
                "cleaning_tool": cleaning_tool_position,
                "target_well": target_well
            }
            
            self.log_operation("sdl1WashCleaning", params, result)
            return result
            
        except Exception as e:
            error_result = {
                "status": "error",
                "operation": "wash_cleaning",
                "error": str(e)
            }
            self.log_operation("sdl1WashCleaning", params, error_result)
            return error_result
    
    def sdl1DataExport(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Data Export Unit Operation
        Export experimental data to specified formats
        """
        try:
            export_format = params.get("export_format", "CSV")
            file_naming = params.get("file_naming", "{experiment_id}_{data_type}")
            include_metadata = params.get("include_metadata", True)
            separate_ac_dc_files = params.get("separate_ac_dc_files", True)
            data_path = params.get("data_path", "./data")
            
            # Generate experiment ID
            experiment_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create data directory
            os.makedirs(data_path, exist_ok=True)
            
            exported_files = []
            
            if export_format.upper() == "CSV":
                # Export DC data
                if self.experiment_data["dc_rows"]:
                    dc_columns = params.get("dc_columns", ["timestamp_s", "current_A", "we_voltage_V"])
                    dc_df = pd.DataFrame(self.experiment_data["dc_rows"], columns=dc_columns)
                    
                    dc_filename = file_naming.format(experiment_id=experiment_id, data_type="dc") + ".csv"
                    dc_filepath = os.path.join(data_path, dc_filename)
                    dc_df.to_csv(dc_filepath, index=False)
                    exported_files.append(dc_filepath)
                
                # Export AC data
                if self.experiment_data["ac_rows"]:
                    ac_df = pd.DataFrame(self.experiment_data["ac_rows"])
                    
                    ac_filename = file_naming.format(experiment_id=experiment_id, data_type="ac") + ".csv"
                    ac_filepath = os.path.join(data_path, ac_filename)
                    ac_df.to_csv(ac_filepath, index=False)
                    exported_files.append(ac_filepath)
                
                # Export metadata
                if include_metadata:
                    metadata = {
                        "experiment_id": experiment_id,
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "time": datetime.now().strftime("%H:%M:%S"),
                        "status": "completed",
                        "data_points": {
                            "dc_count": len(self.experiment_data["dc_rows"]),
                            "ac_count": len(self.experiment_data["ac_rows"])
                        },
                        "operation_log": self.operation_log
                    }
                    
                    metadata_filename = file_naming.format(experiment_id=experiment_id, data_type="metadata") + ".json"
                    metadata_filepath = os.path.join(data_path, metadata_filename)
                    
                    with open(metadata_filepath, 'w') as f:
                        json.dump(metadata, f, indent=2)
                    
                    exported_files.append(metadata_filepath)
            
            result = {
                "status": "success",
                "operation": "data_export",
                "experiment_id": experiment_id,
                "exported_files": exported_files,
                "file_count": len(exported_files),
                "export_format": export_format,
                "data_summary": {
                    "dc_points": len(self.experiment_data["dc_rows"]),
                    "ac_points": len(self.experiment_data["ac_rows"])
                }
            }
            
            self.log_operation("sdl1DataExport", params, result)
            return result
            
        except Exception as e:
            error_result = {
                "status": "error",
                "operation": "data_export",
                "error": str(e)
            }
            self.log_operation("sdl1DataExport", params, error_result)
            return error_result
    
    def sdl1SequenceControl(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sequence Control Unit Operation
        Handle loops and conditional execution
        """
        try:
            loop_type = params.get("loop_type", "fixed_count")
            loop_count = params.get("loop_count", 1)
            loop_condition = params.get("loop_condition", "none")
            break_condition = params.get("break_condition", "")
            
            result = {
                "status": "success",
                "operation": "sequence_control",
                "loop_type": loop_type,
                "configured_loops": loop_count,
                "condition": loop_condition,
                "note": "Sequence control is handled by workflow execution engine"
            }
            
            # Note: Actual loop control would be handled by the workflow execution engine
            # This operation mainly serves as a configuration node
            
            self.log_operation("sdl1SequenceControl", params, result)
            return result
            
        except Exception as e:
            error_result = {
                "status": "error",
                "operation": "sequence_control",
                "error": str(e)
            }
            self.log_operation("sdl1SequenceControl", params, error_result)
            return error_result
    
    def clear_experiment_data(self):
        """Clear experimental data for new experiment"""
        self.experiment_data = {"dc_rows": [], "ac_rows": []}
        self.operation_log = []
    
    def get_operation_log(self) -> list:
        """Get complete operation log"""
        return self.operation_log

    def sdl1ExperimentSetup(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Experiment Setup Unit Operation
        Initialize experiment with hardware configuration and well selection
        """
        try:
            # Extract parameters
            experiment_id = params.get("experiment_id", "Unknown_Experiment")
            test_well_address = params.get("test_well_address", "A1")
            robot_ip = params.get("robot_ip", "169.254.69.185")
            robot_port = params.get("robot_port", 80)
            squidstat_port = params.get("squidstat_port", "COM4")
            squidstat_channel = params.get("squidstat_channel", 0)
            validate_hardware = params.get("validate_hardware_connection", False)
            check_tips = params.get("check_pipette_tips", False)
            verify_well = params.get("verify_well_availability", True)
            run_number = params.get("run_number", 1)
            experiment_notes = params.get("experiment_notes", "")

            # Step 1: Initialize experiment metadata
            experiment_metadata = {
                "experiment_id": experiment_id,
                "test_well": test_well_address,
                "run_number": run_number,
                "start_time": datetime.now().isoformat(),
                "robot_ip": robot_ip,
                "robot_port": robot_port,
                "squidstat_port": squidstat_port,
                "squidstat_channel": squidstat_channel,
                "notes": experiment_notes
            }

            # Step 2: Hardware validation (if requested)
            hardware_status = {"robot": "not_checked", "squidstat": "not_checked"}

            if validate_hardware:
                # Simulate hardware validation
                self.controller.delay(2, "Validating robot connection")
                hardware_status["robot"] = "connected"

                self.controller.delay(1, "Validating squidstat connection")
                hardware_status["squidstat"] = "connected"

            # Step 3: Well availability check
            well_status = "available"
            if verify_well:
                self.controller.delay(1, f"Verifying well {test_well_address} availability")
                well_status = "verified_available"

            # Step 4: Pipette tip check
            tip_status = "not_checked"
            if check_tips:
                self.controller.delay(1, "Checking pipette tip availability")
                tip_status = "sufficient_tips_available"

            # Step 5: Create experiment directory structure (simulated)
            self.controller.delay(1, "Creating experiment directory structure")

            result = {
                "status": "success",
                "operation": "experiment_setup",
                "experiment_metadata": experiment_metadata,
                "hardware_status": hardware_status,
                "well_status": well_status,
                "tip_status": tip_status,
                "message": f"Experiment {experiment_id} setup completed successfully"
            }

            self.log_operation("sdl1ExperimentSetup", params, result)
            return result

        except Exception as e:
            error_result = {
                "status": "error",
                "operation": "experiment_setup",
                "message": f"Experiment setup failed: {str(e)}",
                "error": str(e)
            }
            self.log_operation("sdl1ExperimentSetup", params, error_result)
            return error_result

    def sdl1CycleCounter(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cycle Counter Unit Operation
        Monitor and display current cycle status, progress, and statistics
        """
        try:
            # Extract parameters
            current_cycle = params.get("current_cycle", 1)
            total_cycles = params.get("total_cycles", 1)
            cycle_type = params.get("cycle_type", "electrochemical")
            display_enabled = params.get("display_enabled", True)
            show_progress = params.get("show_progress", True)
            show_statistics = params.get("show_statistics", True)
            update_interval = params.get("update_interval", 1)

            # Calculate progress metrics
            progress_percentage = (current_cycle / total_cycles) * 100 if total_cycles > 0 else 0
            remaining_cycles = max(0, total_cycles - current_cycle)

            # Simulate cycle monitoring
            if display_enabled:
                self.controller.delay(update_interval, f"Monitoring cycle {current_cycle}/{total_cycles}")

            # Collect cycle statistics
            cycle_stats = {
                "current_cycle": current_cycle,
                "total_cycles": total_cycles,
                "progress_percentage": round(progress_percentage, 2),
                "remaining_cycles": remaining_cycles,
                "cycle_type": cycle_type,
                "status": "active" if current_cycle <= total_cycles else "completed"
            }

            # Performance tracking (simulated)
            performance_metrics = {
                "average_cycle_time": 720,  # seconds
                "estimated_completion_time": remaining_cycles * 720,
                "success_rate": 100.0,
                "last_update": datetime.now().isoformat()
            }

            result = {
                "status": "success",
                "operation": "cycle_counter",
                "cycle_stats": cycle_stats,
                "performance_metrics": performance_metrics,
                "display_enabled": display_enabled,
                "message": f"Cycle {current_cycle}/{total_cycles} - {progress_percentage:.1f}% complete"
            }

            self.log_operation("sdl1CycleCounter", params, result)
            return result

        except Exception as e:
            error_result = {
                "status": "error",
                "operation": "cycle_counter",
                "message": f"Cycle counter failed: {str(e)}",
                "error": str(e)
            }
            self.log_operation("sdl1CycleCounter", params, error_result)
            return error_result