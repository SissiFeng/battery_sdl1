"""
Recovery Manager for SDL1 Operations

This module implements checkpoint-based error recovery with hierarchical
recovery strategies for different types of failures.
"""

import json
import logging
import time
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, Callable, List
from pathlib import Path
import traceback


class ErrorSeverity(Enum):
    """Error severity levels for recovery strategy selection"""
    MINOR = "minor"           # Retry current step
    MODERATE = "moderate"     # Restart from checkpoint
    SEVERE = "severe"         # Safe stop, human intervention
    CRITICAL = "critical"     # Emergency stop


class RecoveryAction(Enum):
    """Available recovery actions"""
    RETRY = "retry"
    RESTART_FROM_CHECKPOINT = "restart_from_checkpoint"
    SAFE_STOP = "safe_stop"
    EMERGENCY_STOP = "emergency_stop"
    SKIP_STEP = "skip_step"
    MANUAL_INTERVENTION = "manual_intervention"


class RecoverableError(Exception):
    """Base class for recoverable errors"""
    def __init__(self, message: str, severity: ErrorSeverity, suggested_action: RecoveryAction):
        super().__init__(message)
        self.severity = severity
        self.suggested_action = suggested_action
        self.timestamp = datetime.now()


class PipettingError(RecoverableError):
    """Pipetting operation errors"""
    def __init__(self, message: str):
        super().__init__(message, ErrorSeverity.MINOR, RecoveryAction.RETRY)


class ElectrodeError(RecoverableError):
    """Electrode placement/setup errors"""
    def __init__(self, message: str):
        super().__init__(message, ErrorSeverity.MODERATE, RecoveryAction.RESTART_FROM_CHECKPOINT)


class ElectrochemicalError(RecoverableError):
    """Electrochemical measurement errors"""
    def __init__(self, message: str):
        super().__init__(message, ErrorSeverity.MODERATE, RecoveryAction.RESTART_FROM_CHECKPOINT)


class CriticalSystemError(RecoverableError):
    """Critical system errors requiring immediate attention"""
    def __init__(self, message: str):
        super().__init__(message, ErrorSeverity.CRITICAL, RecoveryAction.EMERGENCY_STOP)


class Checkpoint:
    """Represents a system checkpoint"""
    def __init__(self, name: str, step_index: int, state: Dict[str, Any]):
        self.name = name
        self.step_index = step_index
        self.state = state
        self.timestamp = datetime.now()
        self.id = f"{name}_{int(time.time())}"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "step_index": self.step_index,
            "state": self.state,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Checkpoint':
        checkpoint = cls(data["name"], data["step_index"], data["state"])
        checkpoint.id = data["id"]
        checkpoint.timestamp = datetime.fromisoformat(data["timestamp"])
        return checkpoint


class RecoveryManager:
    """
    Manages checkpoints and error recovery for SDL1 operations
    """
    
    def __init__(self, controller, checkpoint_dir: str = "checkpoints"):
        self.controller = controller
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(exist_ok=True)
        
        self.checkpoints: List[Checkpoint] = []
        self.current_workflow_id: Optional[str] = None
        self.recovery_stats = {
            "total_errors": 0,
            "successful_recoveries": 0,
            "failed_recoveries": 0,
            "manual_interventions": 0
        }
        
        self.logger = logging.getLogger(__name__)
        
        # Define critical checkpoints for SDL1 operations
        self.critical_checkpoints = {
            "experiment_setup_complete",
            "solution_preparation_complete", 
            "electrode_setup_complete",
            "measurement_cycle_complete",
            "cleaning_complete"
        }
    
    def start_workflow(self, workflow_id: str):
        """Start a new workflow with recovery tracking"""
        self.current_workflow_id = workflow_id
        self.checkpoints.clear()
        self.logger.info(f"Started workflow with recovery: {workflow_id}")
    
    def save_checkpoint(self, name: str, step_index: int, state: Dict[str, Any]) -> str:
        """Save a checkpoint with current system state"""
        checkpoint = Checkpoint(name, step_index, state)
        self.checkpoints.append(checkpoint)
        
        # Save to disk for persistence
        checkpoint_file = self.checkpoint_dir / f"{self.current_workflow_id}_{checkpoint.id}.json"
        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint.to_dict(), f, indent=2)
        
        self.logger.info(f"Checkpoint saved: {name} at step {step_index}")
        return checkpoint.id
    
    def get_latest_checkpoint(self, checkpoint_name: Optional[str] = None) -> Optional[Checkpoint]:
        """Get the latest checkpoint, optionally filtered by name"""
        if not self.checkpoints:
            return None
        
        if checkpoint_name:
            matching = [cp for cp in self.checkpoints if cp.name == checkpoint_name]
            return matching[-1] if matching else None
        
        return self.checkpoints[-1]
    
    def restore_from_checkpoint(self, checkpoint: Checkpoint) -> bool:
        """Restore system state from a checkpoint"""
        try:
            self.logger.info(f"Restoring from checkpoint: {checkpoint.name}")
            
            # Restore controller state
            if "robot_state" in checkpoint.state:
                self.controller.restore_state(checkpoint.state["robot_state"])
            
            # Restore experiment state
            if "experiment_data" in checkpoint.state:
                self.controller.restore_experiment_data(checkpoint.state["experiment_data"])
            
            self.logger.info(f"Successfully restored from checkpoint: {checkpoint.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to restore from checkpoint: {str(e)}")
            return False
    
    def run_with_recovery(
        self, 
        step_function: Callable,
        step_name: str,
        step_index: int,
        checkpoint_name: Optional[str] = None,
        max_retries: int = 3,
        **kwargs
    ) -> Any:
        """
        Execute a step with automatic recovery on failure
        
        Args:
            step_function: Function to execute
            step_name: Human-readable step name
            step_index: Step index in workflow
            checkpoint_name: Optional checkpoint to create after success
            max_retries: Maximum retry attempts
            **kwargs: Arguments to pass to step_function
            
        Returns:
            Result of step_function execution
        """
        self.logger.info(f"Executing step with recovery: {step_name}")
        
        for attempt in range(max_retries + 1):
            try:
                # Execute the step
                result = step_function(**kwargs)
                
                # Create checkpoint if specified
                if checkpoint_name:
                    state = {
                        "step_result": result,
                        "robot_state": self.controller.get_state(),
                        "experiment_data": getattr(self.controller, 'experiment_data', {}),
                        "step_name": step_name,
                        "step_index": step_index
                    }
                    self.save_checkpoint(checkpoint_name, step_index, state)
                
                self.logger.info(f"Step completed successfully: {step_name}")
                return result
                
            except RecoverableError as e:
                self.recovery_stats["total_errors"] += 1
                self.logger.warning(f"Recoverable error in {step_name} (attempt {attempt + 1}): {str(e)}")
                
                # Determine recovery action
                recovery_action = self._determine_recovery_action(e, attempt, max_retries)
                
                if recovery_action == RecoveryAction.RETRY:
                    if attempt < max_retries:
                        self.logger.info(f"Retrying step: {step_name}")
                        self._prepare_for_retry(step_name)
                        continue
                    else:
                        self.logger.error(f"Max retries exceeded for step: {step_name}")
                        raise
                
                elif recovery_action == RecoveryAction.RESTART_FROM_CHECKPOINT:
                    if self._restart_from_checkpoint(step_name, step_index):
                        self.recovery_stats["successful_recoveries"] += 1
                        continue
                    else:
                        self.recovery_stats["failed_recoveries"] += 1
                        raise
                
                elif recovery_action == RecoveryAction.SAFE_STOP:
                    self._safe_stop(f"Safe stop triggered by error in {step_name}: {str(e)}")
                    raise
                
                elif recovery_action == RecoveryAction.EMERGENCY_STOP:
                    self._emergency_stop(f"Emergency stop triggered by critical error: {str(e)}")
                    raise
                
                elif recovery_action == RecoveryAction.MANUAL_INTERVENTION:
                    self.recovery_stats["manual_interventions"] += 1
                    self._request_manual_intervention(step_name, e)
                    raise
            
            except Exception as e:
                # Non-recoverable error
                self.logger.error(f"Non-recoverable error in {step_name}: {str(e)}")
                self.logger.error(f"Traceback: {traceback.format_exc()}")
                self._safe_stop(f"Non-recoverable error in {step_name}")
                raise CriticalSystemError(f"Non-recoverable error: {str(e)}")
        
        # Should not reach here
        raise CriticalSystemError(f"Unexpected error in recovery loop for {step_name}")
    
    def _determine_recovery_action(
        self, 
        error: RecoverableError, 
        attempt: int, 
        max_retries: int
    ) -> RecoveryAction:
        """Determine the appropriate recovery action based on error and context"""
        
        # Use error's suggested action as starting point
        suggested = error.suggested_action
        
        # Modify based on attempt count and severity
        if error.severity == ErrorSeverity.MINOR:
            if attempt < max_retries:
                return RecoveryAction.RETRY
            else:
                return RecoveryAction.RESTART_FROM_CHECKPOINT
        
        elif error.severity == ErrorSeverity.MODERATE:
            if attempt == 0:
                return RecoveryAction.RETRY
            else:
                return RecoveryAction.RESTART_FROM_CHECKPOINT
        
        elif error.severity == ErrorSeverity.SEVERE:
            return RecoveryAction.SAFE_STOP
        
        elif error.severity == ErrorSeverity.CRITICAL:
            return RecoveryAction.EMERGENCY_STOP
        
        return suggested
    
    def _prepare_for_retry(self, step_name: str):
        """Prepare system for retry attempt"""
        self.logger.info(f"Preparing for retry: {step_name}")
        
        # Add small delay to allow system to stabilize
        time.sleep(2)
        
        # Clear any error states
        if hasattr(self.controller, 'clear_error_state'):
            self.controller.clear_error_state()
    
    def _restart_from_checkpoint(self, step_name: str, step_index: int) -> bool:
        """Restart from the most recent appropriate checkpoint"""
        self.logger.info(f"Attempting restart from checkpoint for step: {step_name}")
        
        # Find the most recent checkpoint before this step
        suitable_checkpoint = None
        for checkpoint in reversed(self.checkpoints):
            if checkpoint.step_index < step_index:
                suitable_checkpoint = checkpoint
                break
        
        if suitable_checkpoint:
            return self.restore_from_checkpoint(suitable_checkpoint)
        else:
            self.logger.warning("No suitable checkpoint found for restart")
            return False
    
    def _safe_stop(self, reason: str):
        """Perform safe stop of all operations"""
        self.logger.warning(f"Performing safe stop: {reason}")
        
        try:
            # Stop all robot movements
            if hasattr(self.controller, 'stop_all_movements'):
                self.controller.stop_all_movements()
            
            # Turn off heating/cooling
            if hasattr(self.controller, 'disable_temperature_control'):
                self.controller.disable_temperature_control()
            
            # Save current state
            self._save_emergency_state()
            
        except Exception as e:
            self.logger.error(f"Error during safe stop: {str(e)}")
    
    def _emergency_stop(self, reason: str):
        """Perform emergency stop of all operations"""
        self.logger.critical(f"EMERGENCY STOP: {reason}")
        
        try:
            # Immediate stop of all operations
            if hasattr(self.controller, 'emergency_stop'):
                self.controller.emergency_stop()
            
            # Save emergency state
            self._save_emergency_state()
            
        except Exception as e:
            self.logger.critical(f"Error during emergency stop: {str(e)}")
    
    def _request_manual_intervention(self, step_name: str, error: RecoverableError):
        """Request manual intervention from operator"""
        self.logger.warning(f"Manual intervention required for step: {step_name}")
        self.logger.warning(f"Error details: {str(error)}")
        
        # Save current state for operator review
        self._save_emergency_state()
        
        # Could integrate with notification system here
        # e.g., send email, SMS, or dashboard alert
    
    def _save_emergency_state(self):
        """Save current system state for emergency recovery"""
        try:
            emergency_state = {
                "timestamp": datetime.now().isoformat(),
                "workflow_id": self.current_workflow_id,
                "robot_state": self.controller.get_state(),
                "experiment_data": getattr(self.controller, 'experiment_data', {}),
                "checkpoints": [cp.to_dict() for cp in self.checkpoints],
                "recovery_stats": self.recovery_stats
            }
            
            emergency_file = self.checkpoint_dir / f"emergency_{self.current_workflow_id}_{int(time.time())}.json"
            with open(emergency_file, 'w') as f:
                json.dump(emergency_state, f, indent=2)
            
            self.logger.info(f"Emergency state saved: {emergency_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save emergency state: {str(e)}")
    
    def get_recovery_statistics(self) -> Dict[str, Any]:
        """Get recovery performance statistics"""
        total_operations = (
            self.recovery_stats["successful_recoveries"] + 
            self.recovery_stats["failed_recoveries"]
        )
        
        success_rate = (
            self.recovery_stats["successful_recoveries"] / total_operations * 100
            if total_operations > 0 else 0
        )
        
        return {
            **self.recovery_stats,
            "success_rate": round(success_rate, 2),
            "total_checkpoints": len(self.checkpoints),
            "workflow_id": self.current_workflow_id
        }
    
    def cleanup_old_checkpoints(self, max_age_hours: int = 24):
        """Clean up old checkpoint files"""
        cutoff_time = time.time() - (max_age_hours * 3600)
        
        for checkpoint_file in self.checkpoint_dir.glob("*.json"):
            if checkpoint_file.stat().st_mtime < cutoff_time:
                checkpoint_file.unlink()
                self.logger.info(f"Cleaned up old checkpoint: {checkpoint_file}")
