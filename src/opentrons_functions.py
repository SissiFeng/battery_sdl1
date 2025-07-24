"""
Modular Opentrons Function Library
Extracted from the manual electrodeposition script for API automation
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, Optional, List, Any
from opentrons import opentronsClient


class OpentronsController:
    """
    Modular controller for Opentrons operations
    Provides reusable functions for Canvas workflow automation
    """
    
    def __init__(self, robot_ip: str = "169.254.69.185", dry_run: bool = False):
        self.robot_ip = robot_ip
        self.dry_run = dry_run
        self.client = None
        self.labware_registry = {}
        self.pipette_tip_counter = 1
        
        if not dry_run:
            self.client = opentronsClient(strRobotIP=robot_ip)
    
    def log_operation(self, operation: str, params: Dict):
        """Log operation for debugging and monitoring"""
        if self.dry_run:
            logging.info(f"[DRY RUN] {operation}: {params}")
        else:
            logging.info(f"[EXECUTING] {operation}: {params}")
    
    # SETUP OPERATIONS
    def initialize_robot(self) -> Dict[str, Any]:
        """Initialize robot and home all axes"""
        self.log_operation("initialize_robot", {})
        
        if not self.dry_run and self.client:
            self.client.lights(True)
            self.client.homeRobot()
        
        return {"status": "success", "message": "Robot initialized"}
    
    def load_labware(self, slot: int, labware_name: str, labware_id: Optional[str] = None) -> str:
        """Load standard Opentrons labware"""
        params = {"slot": slot, "labware_name": labware_name}
        self.log_operation("load_labware", params)
        
        if self.dry_run:
            labware_id = f"mock_{labware_name}_slot{slot}"
        elif self.client:
            labware_id = self.client.loadLabware(strSlot=slot, strLabwareName=labware_name)
        
        self.labware_registry[f"slot_{slot}"] = {
            "id": labware_id,
            "name": labware_name,
            "type": "standard"
        }
        
        return labware_id
    
    def load_custom_labware(self, slot: int, labware_file_path: str) -> str:
        """Load custom labware from JSON file"""
        params = {"slot": slot, "labware_file": labware_file_path}
        self.log_operation("load_custom_labware", params)
        
        if self.dry_run:
            labware_id = f"mock_custom_slot{slot}"
        else:
            with open(labware_file_path) as f:
                labware_dict = json.load(f)
            labware_id = self.client.loadCustomLabware(dicLabware=labware_dict, strSlot=slot)
        
        self.labware_registry[f"slot_{slot}"] = {
            "id": labware_id,
            "name": os.path.basename(labware_file_path),
            "type": "custom"
        }
        
        return labware_id
    
    def load_pipette(self, pipette_name: str, mount: str) -> Dict[str, Any]:
        """Load pipette on specified mount"""
        params = {"pipette_name": pipette_name, "mount": mount}
        self.log_operation("load_pipette", params)
        
        if not self.dry_run and self.client:
            self.client.loadPipette(strPipetteName=pipette_name, strMount=mount)
        
        return {"status": "success", "pipette": pipette_name, "mount": mount}
    
    # MOVEMENT OPERATIONS
    def move_to_well(self, labware_name: str, well_name: str, pipette_name: str,
                     offset_start: str = "top", offset_x: float = 0, offset_y: float = 0,
                     offset_z: float = 0, speed: int = 100) -> Dict[str, Any]:
        """Move pipette to specified well"""
        params = {
            "labware": labware_name, "well": well_name, "pipette": pipette_name,
            "offset_start": offset_start, "offset_x": offset_x, "offset_y": offset_y,
            "offset_z": offset_z, "speed": speed
        }
        self.log_operation("move_to_well", params)
        
        if not self.dry_run and self.client:
            self.client.moveToWell(
                strLabwareName=labware_name,
                strWellName=well_name,
                strPipetteName=pipette_name,
                strOffsetStart=offset_start,
                fltOffsetX=offset_x,
                fltOffsetY=offset_y,
                fltOffsetZ=offset_z,
                intSpeed=speed
            )
        
        return {"status": "success", "position": f"{labware_name}:{well_name}"}
    
    # LIQUID HANDLING OPERATIONS
    def aspirate(self, labware_name: str, well_name: str, pipette_name: str,
                 volume: int, offset_start: str = "bottom", offset_x: float = 0,
                 offset_y: float = 0, offset_z: float = 0) -> Dict[str, Any]:
        """Aspirate liquid from well"""
        params = {
            "labware": labware_name, "well": well_name, "pipette": pipette_name,
            "volume": volume, "offset_start": offset_start, "offset_x": offset_x,
            "offset_y": offset_y, "offset_z": offset_z
        }
        self.log_operation("aspirate", params)
        
        if not self.dry_run and self.client:
            self.client.aspirate(
                strLabwareName=labware_name,
                strWellName=well_name,
                strPipetteName=pipette_name,
                intVolume=volume,
                strOffsetStart=offset_start,
                fltOffsetX=offset_x,
                fltOffsetY=offset_y,
                fltOffsetZ=offset_z
            )
        
        return {"status": "success", "volume_aspirated": volume}
    
    def dispense(self, labware_name: str, well_name: str, pipette_name: str,
                 volume: int, offset_start: str = "top", offset_x: float = 0,
                 offset_y: float = 0, offset_z: float = 0) -> Dict[str, Any]:
        """Dispense liquid to well"""
        params = {
            "labware": labware_name, "well": well_name, "pipette": pipette_name,
            "volume": volume, "offset_start": offset_start, "offset_x": offset_x,
            "offset_y": offset_y, "offset_z": offset_z
        }
        self.log_operation("dispense", params)
        
        if not self.dry_run and self.client:
            self.client.dispense(
                strLabwareName=labware_name,
                strWellName=well_name,
                strPipetteName=pipette_name,
                intVolume=volume,
                strOffsetStart=offset_start,
                fltOffsetX=offset_x,
                fltOffsetY=offset_y,
                fltOffsetZ=offset_z
            )
        
        return {"status": "success", "volume_dispensed": volume}
    
    def blowout(self, labware_name: str, well_name: str, pipette_name: str,
                offset_start: str = "top", offset_x: float = 0, offset_y: float = 0,
                offset_z: float = 0) -> Dict[str, Any]:
        """Blowout remaining liquid"""
        params = {
            "labware": labware_name, "well": well_name, "pipette": pipette_name,
            "offset_start": offset_start, "offset_x": offset_x, "offset_y": offset_y,
            "offset_z": offset_z
        }
        self.log_operation("blowout", params)
        
        if not self.dry_run and self.client:
            self.client.blowout(
                strLabwareName=labware_name,
                strWellName=well_name,
                strPipetteName=pipette_name,
                strOffsetStart=offset_start,
                fltOffsetX=offset_x,
                fltOffsetY=offset_y,
                fltOffsetZ=offset_z
            )
        
        return {"status": "success", "operation": "blowout"}
    
    def fill_well(self, source_labware: str, source_well: str, dest_labware: str,
                  dest_well: str, pipette_name: str, volume: int,
                  offset_start_from: str = "bottom", offset_start_to: str = "top",
                  offset_x_from: float = 0, offset_y_from: float = 0, offset_z_from: float = 0,
                  offset_x_to: float = 0, offset_y_to: float = 0, offset_z_to: float = 0,
                  move_speed: int = 100) -> Dict[str, Any]:
        """
        High-level function to transfer large volumes (>1000μL) with multiple cycles
        Based on the fillWell function from the original script
        """
        params = {
            "source": f"{source_labware}:{source_well}",
            "dest": f"{dest_labware}:{dest_well}",
            "volume": volume,
            "pipette": pipette_name
        }
        self.log_operation("fill_well", params)
        
        if self.dry_run:
            cycles = max(1, volume // 1000)
            remaining = volume % 1000 if volume > 1000 else volume
            return {
                "status": "success",
                "cycles": cycles,
                "remaining_volume": remaining,
                "total_volume": volume
            }
        
        # Actual implementation for multi-cycle transfer
        remaining_volume = volume
        cycles = 0
        
        while remaining_volume > 1000:
            # Transfer 1000 μL
            self.move_to_well(source_labware, source_well, pipette_name, "top",
                            offset_x_from, offset_y_from, 0, move_speed)
            self.aspirate(source_labware, source_well, pipette_name, 1000,
                        offset_start_from, offset_x_from, offset_y_from, offset_z_from)
            self.move_to_well(dest_labware, dest_well, pipette_name, "top",
                            offset_x_to, offset_y_to, 0, move_speed)
            self.dispense(dest_labware, dest_well, pipette_name, 1000,
                        offset_start_to, offset_x_to, offset_y_to, offset_z_to)
            self.blowout(dest_labware, dest_well, pipette_name, offset_start_to,
                       offset_x_to, offset_y_to, offset_z_to)
            
            remaining_volume -= 1000
            cycles += 1
        
        # Transfer remaining volume
        if remaining_volume > 0:
            self.move_to_well(source_labware, source_well, pipette_name, "top",
                            offset_x_from, offset_y_from, 0, move_speed)
            self.aspirate(source_labware, source_well, pipette_name, remaining_volume,
                        offset_start_from, offset_x_from, offset_y_from, offset_z_from)
            self.move_to_well(dest_labware, dest_well, pipette_name, "top",
                            offset_x_to, offset_y_to, 0, move_speed)
            self.dispense(dest_labware, dest_well, pipette_name, remaining_volume,
                        offset_start_to, offset_x_to, offset_y_to, offset_z_to)
            self.blowout(dest_labware, dest_well, pipette_name, offset_start_to,
                       offset_x_to, offset_y_to, offset_z_to)
        
        return {
            "status": "success",
            "cycles": cycles,
            "total_volume": volume,
            "final_transfer": remaining_volume
        }
    
    # TIP OPERATIONS
    def pickup_tip(self, labware_name: str, well_name: str, pipette_name: str,
                   offset_x: float = 0, offset_y: float = 0) -> Dict[str, Any]:
        """Pick up pipette tip"""
        params = {
            "labware": labware_name, "well": well_name, "pipette": pipette_name,
            "offset_x": offset_x, "offset_y": offset_y
        }
        self.log_operation("pickup_tip", params)
        
        if not self.dry_run and self.client:
            self.client.pickUpTip(
                strLabwareName=labware_name,
                strPipetteName=pipette_name,
                strWellName=well_name,
                fltOffsetX=offset_x,
                fltOffsetY=offset_y
            )
        
        return {"status": "success", "tip_location": f"{labware_name}:{well_name}"}
    
    def drop_tip(self, labware_name: str, well_name: str, pipette_name: str,
                 offset_start: str = "bottom", offset_x: float = 0, offset_y: float = 0,
                 offset_z: float = 0, drop_in_disposal: bool = True) -> Dict[str, Any]:
        """Drop pipette tip"""
        params = {
            "labware": labware_name, "well": well_name, "pipette": pipette_name,
            "drop_in_disposal": drop_in_disposal
        }
        self.log_operation("drop_tip", params)
        
        if not self.dry_run and self.client:
            self.client.dropTip(
                strLabwareName=labware_name,
                strPipetteName=pipette_name,
                strWellName=well_name,
                strOffsetStart=offset_start,
                fltOffsetX=offset_x,
                fltOffsetY=offset_y,
                fltOffsetZ=offset_z,
                boolDropInDisposal=drop_in_disposal
            )
        
        return {"status": "success", "operation": "tip_dropped"}
    
    # UTILITY OPERATIONS
    def delay(self, seconds: float, message: str = "") -> Dict[str, Any]:
        """Wait for specified time"""
        params = {"seconds": seconds, "message": message}
        self.log_operation("delay", params)
        
        if not self.dry_run:
            import time
            time.sleep(seconds)
        
        return {"status": "success", "delay": seconds}
    
    def get_pipette_tip_location(self, tip_id: int) -> str:
        """Convert tip ID to well location (A1, A2, etc.)"""
        if tip_id > 96 or tip_id < 1:
            raise ValueError("Tip ID must be between 1 and 96")
        
        row = chr(ord('A') + ((tip_id - 1) // 12))
        col = (tip_id - 1) % 12 + 1
        return f"{row}{col}"
    
    def home_robot(self) -> Dict[str, Any]:
        """Home all robot axes"""
        self.log_operation("home_robot", {})
        
        if not self.dry_run and self.client:
            self.client.homeRobot()
        
        return {"status": "success", "operation": "robot_homed"}
    
    def set_lights(self, on: bool) -> Dict[str, Any]:
        """Control robot lights"""
        params = {"lights_on": on}
        self.log_operation("set_lights", params)
        
        if not self.dry_run and self.client:
            self.client.lights(on)
        
        return {"status": "success", "lights": "on" if on else "off"}
    
    # STATUS OPERATIONS
    def get_status(self) -> Dict[str, Any]:
        """Get current robot status"""
        return {
            "robot_ip": self.robot_ip,
            "dry_run": self.dry_run,
            "connected": self.client is not None,
            "labware_count": len(self.labware_registry),
            "tip_counter": self.pipette_tip_counter
        }
    
    def get_labware_registry(self) -> Dict[str, Any]:
        """Get all loaded labware"""
        return self.labware_registry