"""
Battery SDL1 - Opentrons Workflow Mapper

A comprehensive workflow mapping system for SDL1 operations.
"""

__version__ = "2.0.0"
__author__ = "SDL1 Development Team"
__description__ = "Workflow mapping system for automated battery research"

# Import main classes for easy access
try:
    from .workflow_mapper import WorkflowMapper
    from .sdl1_operations import SDL1Operations
    from .opentrons_functions import OpentronsController
    
    __all__ = [
        'WorkflowMapper',
        'SDL1Operations', 
        'OpentronsController'
    ]
except ImportError:
    # Handle case where dependencies are not available
    __all__ = []
