"""
Workflow Manager Factory for Battery SDL1

This module provides a factory for creating workflow managers,
allowing users to choose between native implementation and Prefect-based management.
"""

import logging
from enum import Enum
from typing import Dict, Any, Optional, Union

from .opentrons_functions import OpentronsController
from .workflow_mapper import WorkflowMapper

# Try to import Prefect components
try:
    from .prefect_workflow_manager import PrefectWorkflowManager
    from .prefect_deployment_manager import PrefectDeploymentManager
    PREFECT_AVAILABLE = True
except ImportError:
    PREFECT_AVAILABLE = False
    PrefectWorkflowManager = None
    PrefectDeploymentManager = None


class WorkflowManagerType(Enum):
    """Enumeration of available workflow manager types"""
    NATIVE = "native"
    PREFECT = "prefect"


class WorkflowManagerFactory:
    """
    Factory class for creating workflow managers
    Provides a unified interface for different workflow management backends
    """
    
    @staticmethod
    def create_manager(
        manager_type: Union[WorkflowManagerType, str],
        controller: OpentronsController,
        **kwargs
    ) -> Union[WorkflowMapper, PrefectWorkflowManager]:
        """
        Create a workflow manager of the specified type
        
        Args:
            manager_type: Type of workflow manager to create
            controller: OpentronsController instance
            **kwargs: Additional arguments for manager initialization
            
        Returns:
            Workflow manager instance
            
        Raises:
            ValueError: If manager type is not supported
            ImportError: If required dependencies are not available
        """
        if isinstance(manager_type, str):
            try:
                manager_type = WorkflowManagerType(manager_type.lower())
            except ValueError:
                raise ValueError(f"Unknown manager type: {manager_type}")
        
        if manager_type == WorkflowManagerType.NATIVE:
            return WorkflowMapper(controller)
        
        elif manager_type == WorkflowManagerType.PREFECT:
            if not PREFECT_AVAILABLE:
                raise ImportError(
                    "Prefect is not available. Install with: pip install prefect>=2.10.0"
                )
            return PrefectWorkflowManager(controller)
        
        else:
            raise ValueError(f"Unsupported manager type: {manager_type}")
    
    @staticmethod
    def create_deployment_manager(
        controller: OpentronsController,
        **kwargs
    ) -> Optional[PrefectDeploymentManager]:
        """
        Create a Prefect deployment manager
        
        Args:
            controller: OpentronsController instance
            **kwargs: Additional arguments for manager initialization
            
        Returns:
            PrefectDeploymentManager instance or None if Prefect not available
            
        Raises:
            ImportError: If Prefect is not available
        """
        if not PREFECT_AVAILABLE:
            raise ImportError(
                "Prefect is not available. Install with: pip install prefect>=2.10.0"
            )
        
        return PrefectDeploymentManager(controller)
    
    @staticmethod
    def get_available_managers() -> Dict[str, Dict[str, Any]]:
        """
        Get information about available workflow managers
        
        Returns:
            Dictionary with manager information
        """
        managers = {
            "native": {
                "name": "Native Workflow Manager",
                "description": "Built-in workflow management with basic task execution",
                "available": True,
                "features": [
                    "Sequential task execution",
                    "Basic error handling",
                    "Operation logging",
                    "Canvas JSON support"
                ],
                "requirements": ["None (built-in)"]
            }
        }
        
        if PREFECT_AVAILABLE:
            managers["prefect"] = {
                "name": "Prefect Workflow Manager",
                "description": "Advanced workflow orchestration with Prefect",
                "available": True,
                "features": [
                    "Advanced task orchestration",
                    "Automatic retries and error handling",
                    "Workflow scheduling and monitoring",
                    "Parallel and sequential execution",
                    "Web UI for monitoring",
                    "Deployment management",
                    "Flow versioning",
                    "Task caching"
                ],
                "requirements": ["prefect>=2.10.0", "prefect-shell>=0.1.0"]
            }
        else:
            managers["prefect"] = {
                "name": "Prefect Workflow Manager",
                "description": "Advanced workflow orchestration with Prefect",
                "available": False,
                "features": [
                    "Advanced task orchestration",
                    "Automatic retries and error handling", 
                    "Workflow scheduling and monitoring",
                    "Parallel and sequential execution",
                    "Web UI for monitoring",
                    "Deployment management"
                ],
                "requirements": ["prefect>=2.10.0", "prefect-shell>=0.1.0"],
                "install_command": "pip install prefect>=2.10.0 prefect-shell>=0.1.0"
            }
        
        return managers
    
    @staticmethod
    def recommend_manager(
        use_case: str = "basic",
        requirements: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Recommend a workflow manager based on use case and requirements
        
        Args:
            use_case: Type of use case ("basic", "production", "research", "development")
            requirements: Optional requirements dictionary
            
        Returns:
            Recommendation with manager type and reasoning
        """
        requirements = requirements or {}
        
        # Basic use case - simple workflow execution
        if use_case == "basic":
            return {
                "recommended": WorkflowManagerType.NATIVE.value,
                "reasoning": "Native manager is sufficient for basic workflow execution",
                "alternative": WorkflowManagerType.PREFECT.value if PREFECT_AVAILABLE else None
            }
        
        # Production use case - reliability and monitoring needed
        elif use_case == "production":
            if PREFECT_AVAILABLE:
                return {
                    "recommended": WorkflowManagerType.PREFECT.value,
                    "reasoning": "Prefect provides production-grade features like monitoring, retries, and scheduling",
                    "alternative": WorkflowManagerType.NATIVE.value
                }
            else:
                return {
                    "recommended": WorkflowManagerType.NATIVE.value,
                    "reasoning": "Native manager available (install Prefect for production features)",
                    "alternative": None,
                    "suggestion": "Install Prefect for production use: pip install prefect>=2.10.0"
                }
        
        # Research use case - flexibility and experimentation
        elif use_case == "research":
            return {
                "recommended": WorkflowManagerType.NATIVE.value,
                "reasoning": "Native manager provides flexibility for research and experimentation",
                "alternative": WorkflowManagerType.PREFECT.value if PREFECT_AVAILABLE else None
            }
        
        # Development use case - debugging and iteration
        elif use_case == "development":
            if PREFECT_AVAILABLE:
                return {
                    "recommended": WorkflowManagerType.PREFECT.value,
                    "reasoning": "Prefect provides excellent debugging and monitoring capabilities",
                    "alternative": WorkflowManagerType.NATIVE.value
                }
            else:
                return {
                    "recommended": WorkflowManagerType.NATIVE.value,
                    "reasoning": "Native manager suitable for development (Prefect adds monitoring)",
                    "alternative": None
                }
        
        # Default recommendation
        else:
            return {
                "recommended": WorkflowManagerType.NATIVE.value,
                "reasoning": "Native manager is the default choice",
                "alternative": WorkflowManagerType.PREFECT.value if PREFECT_AVAILABLE else None
            }


class UnifiedWorkflowInterface:
    """
    Unified interface for workflow execution regardless of backend
    Provides a consistent API for both native and Prefect managers
    """
    
    def __init__(
        self,
        manager_type: Union[WorkflowManagerType, str] = WorkflowManagerType.NATIVE,
        controller: Optional[OpentronsController] = None,
        **kwargs
    ):
        self.manager_type = manager_type
        self.controller = controller or OpentronsController(dry_run=True)
        self.manager = WorkflowManagerFactory.create_manager(
            manager_type, self.controller, **kwargs
        )
        self.logger = logging.getLogger(__name__)
    
    def execute_workflow(self, workflow_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a workflow using the configured manager
        
        Args:
            workflow_json: Canvas workflow JSON
            
        Returns:
            Execution results
        """
        if isinstance(self.manager, WorkflowMapper):
            # Native manager
            return self.manager.execute_canvas_workflow(workflow_json)
        
        elif hasattr(self.manager, 'execute_canvas_workflow_flow'):
            # Prefect manager - run the flow synchronously
            try:
                # For Prefect, we need to run the flow
                flow_func = self.manager.execute_canvas_workflow_flow
                return flow_func(workflow_json)
            except Exception as e:
                self.logger.error(f"Prefect workflow execution failed: {str(e)}")
                return {
                    "status": "error",
                    "message": f"Workflow execution failed: {str(e)}",
                    "manager_type": str(self.manager_type)
                }
        
        else:
            raise ValueError(f"Unknown manager type: {type(self.manager)}")
    
    def get_manager_info(self) -> Dict[str, Any]:
        """Get information about the current manager"""
        return {
            "type": str(self.manager_type),
            "class": self.manager.__class__.__name__,
            "features": WorkflowManagerFactory.get_available_managers().get(
                str(self.manager_type), {}
            ).get("features", [])
        }
