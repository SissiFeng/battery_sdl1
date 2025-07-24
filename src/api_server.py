"""
FastAPI Backend Server for Opentrons Workflow Automation
Receives JSON workflows from Canvas frontend and executes them
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import logging
import os
from datetime import datetime
import uvicorn

from opentrons_functions import OpentronsController
from workflow_mapper import WorkflowMapper
from workflow_manager_factory import WorkflowManagerFactory, UnifiedWorkflowInterface, WorkflowManagerType

# Try to import Prefect components
try:
    from prefect_deployment_manager import PrefectDeploymentManager
    PREFECT_AVAILABLE = True
except ImportError:
    PREFECT_AVAILABLE = False
    PrefectDeploymentManager = None


# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(f"opentrons_api_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)

app = FastAPI(
    title="Opentrons Workflow API",
    description="API for executing Canvas-generated workflows on Opentrons robots",
    version="1.0.0"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
controller: Optional[OpentronsController] = None
mapper: Optional[WorkflowMapper] = None
current_manager_type: str = "native"  # Default to native manager
deployment_manager: Optional[Any] = None  # Prefect deployment manager


# Pydantic models for API
class WorkflowNode(BaseModel):
    type: str
    params: Dict[str, Any] = {}


class Workflow(BaseModel):
    nodes: List[WorkflowNode]
    metadata: Optional[Dict[str, Any]] = {}


class CanvasWorkflow(BaseModel):
    """Canvas-specific workflow format"""
    metadata: Dict[str, Any]
    workflow: Dict[str, Any]


class ExecutionConfig(BaseModel):
    dry_run: bool = False
    robot_ip: str = "169.254.69.185"
    continue_on_error: bool = True
    save_results: bool = True


class ManagerConfig(BaseModel):
    """Configuration for workflow manager selection"""
    manager_type: str = "native"  # "native" or "prefect"
    dry_run: bool = False
    robot_ip: str = "169.254.69.185"


class PrefectDeploymentConfig(BaseModel):
    """Configuration for Prefect deployment"""
    deployment_name: str
    workflow_file: str
    schedule: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None


class ExecutionRequest(BaseModel):
    workflow: Workflow
    config: ExecutionConfig = ExecutionConfig()


class CanvasExecutionRequest(BaseModel):
    """Canvas-specific execution request"""
    canvas_workflow: CanvasWorkflow
    config: ExecutionConfig = ExecutionConfig()


# API Endpoints
@app.on_event("startup")
async def startup_event():
    """Initialize controller and mapper on startup"""
    global controller, mapper
    logging.info("Starting Opentrons Workflow API with SDL1 support...")
    
    # Initialize with default settings (can be overridden per request)
    controller = OpentronsController(dry_run=True)  # Default to dry run for safety
    mapper = WorkflowMapper(controller)
    
    # Setup required labware for SDL1 operations
    await setup_sdl1_labware()
    
    logging.info("API startup complete")


async def setup_sdl1_labware():
    """Setup required labware for SDL1 operations"""
    global controller
    
    try:
        if controller and controller.dry_run:
            # In dry run mode, load mock labware
            controller.load_labware(1, "opentrons_96_tiprack_1000ul")
            controller.load_custom_labware(2, "./labware/nis_8_reservoir_25000ul.json")
            controller.load_custom_labware(9, "./labware/nis_15_wellplate_3895ul.json") 
            controller.load_custom_labware(10, "./labware/nistall_4_tiprack_1ul.json")
            controller.load_pipette("p1000_single_gen2", "right")
            
            logging.info("SDL1 labware setup completed (dry run mode)")
        
    except Exception as e:
        logging.warning(f"SDL1 labware setup failed: {str(e)} - continuing without pre-setup")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Opentrons Workflow API",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    global controller, mapper
    
    return {
        "api_status": "healthy",
        "controller_initialized": controller is not None,
        "mapper_initialized": mapper is not None,
        "controller_status": controller.get_status() if controller else None,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/operations")
async def get_supported_operations():
    """Get list of all supported workflow operations"""
    global mapper
    
    if not mapper:
        raise HTTPException(status_code=500, detail="Mapper not initialized")
    
    operations = mapper.get_supported_operations()
    
    return {
        "supported_operations": operations,
        "count": len(operations),
        "timestamp": datetime.now().isoformat()
    }


@app.post("/validate")
async def validate_workflow(workflow: Workflow):
    """Validate workflow without executing"""
    global mapper
    
    if not mapper:
        raise HTTPException(status_code=500, detail="Mapper not initialized")
    
    # Convert Pydantic models to dict
    workflow_nodes = [node.dict() for node in workflow.nodes]
    
    validation_result = mapper.validate_workflow(workflow_nodes)
    
    return {
        "validation": validation_result,
        "workflow_info": {
            "total_nodes": len(workflow.nodes),
            "metadata": workflow.metadata
        },
        "timestamp": datetime.now().isoformat()
    }


@app.post("/execute")
async def execute_workflow(request: ExecutionRequest):
    """Execute workflow with specified configuration"""
    global controller, mapper
    
    # Reinitialize controller with request-specific settings
    controller = OpentronsController(
        robot_ip=request.config.robot_ip,
        dry_run=request.config.dry_run
    )
    mapper = WorkflowMapper(controller)
    
    # Validate workflow first
    workflow_nodes = [node.dict() for node in request.workflow.nodes]
    validation_result = mapper.validate_workflow(workflow_nodes)
    
    if not validation_result["valid"]:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Workflow validation failed",
                "validation_errors": validation_result["errors"]
            }
        )
    
    # Execute workflow
    try:
        execution_result = mapper.execute_workflow(workflow_nodes)
        
        # Save results if requested
        if request.config.save_results:
            await save_execution_results(request, execution_result)
        
        return {
            "execution": execution_result,
            "config": request.config.dict(),
            "workflow_info": {
                "total_nodes": len(request.workflow.nodes),
                "metadata": request.workflow.metadata
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Workflow execution failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Workflow execution failed",
                "message": str(e)
            }
        )


@app.post("/execute/dry-run")
async def execute_dry_run(workflow: Workflow):
    """Execute workflow in dry-run mode (simulation only)"""
    request = ExecutionRequest(
        workflow=workflow,
        config=ExecutionConfig(dry_run=True)
    )
    return await execute_workflow(request)


@app.post("/canvas/execute")
async def execute_canvas_workflow(request: CanvasExecutionRequest):
    """Execute Canvas workflow with SDL1 operations"""
    global controller, mapper
    
    # Reinitialize controller with request-specific settings
    controller = OpentronsController(
        robot_ip=request.config.robot_ip,
        dry_run=request.config.dry_run
    )
    mapper = WorkflowMapper(controller)
    
    # Execute Canvas workflow
    try:
        canvas_json = request.canvas_workflow.dict()
        execution_result = mapper.execute_canvas_workflow(canvas_json)
        
        # Save results if requested
        if request.config.save_results:
            await save_execution_results_canvas(request, execution_result)
        
        return {
            "execution": execution_result,
            "config": request.config.dict(),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Canvas workflow execution failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Canvas workflow execution failed",
                "message": str(e)
            }
        )


@app.post("/canvas/execute/dry-run")
async def execute_canvas_dry_run(canvas_workflow: CanvasWorkflow):
    """Execute Canvas workflow in dry-run mode"""
    request = CanvasExecutionRequest(
        canvas_workflow=canvas_workflow,
        config=ExecutionConfig(dry_run=True)
    )
    return await execute_canvas_workflow(request)


@app.post("/canvas/validate")
async def validate_canvas_workflow(canvas_workflow: CanvasWorkflow):
    """Validate Canvas workflow without executing"""
    global mapper
    
    if not mapper:
        raise HTTPException(status_code=500, detail="Mapper not initialized")
    
    try:
        # Extract nodes from Canvas structure
        workflow_data = canvas_workflow.workflow
        nodes = workflow_data.get("nodes", [])
        
        # Validate using existing method
        validation_result = mapper.validate_workflow(nodes)
        
        return {
            "validation": validation_result,
            "workflow_info": {
                "total_nodes": len(nodes),
                "workflow_name": canvas_workflow.metadata.get("name", "Unnamed"),
                "workflow_id": canvas_workflow.metadata.get("id", "unknown"),
                "metadata": canvas_workflow.metadata
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Canvas validation failed",
                "message": str(e)
            }
        )


@app.post("/upload")
async def upload_workflow_file(file: UploadFile = File(...)):
    """Upload and validate JSON workflow file"""
    try:
        # Read file content
        content = await file.read()
        workflow_data = json.loads(content)
        
        # Validate JSON structure
        if "nodes" not in workflow_data:
            raise HTTPException(
                status_code=400,
                detail="Invalid workflow format: missing 'nodes' field"
            )
        
        # Convert to Workflow model
        workflow = Workflow(**workflow_data)
        
        # Validate workflow
        validation_result = await validate_workflow(workflow)
        
        return {
            "upload": {
                "filename": file.filename,
                "size": len(content),
                "status": "success"
            },
            "validation": validation_result["validation"],
            "workflow_info": {
                "total_nodes": len(workflow.nodes),
                "metadata": workflow.metadata
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid JSON format",
                "message": str(e)
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "File processing failed",
                "message": str(e)
            }
        )


@app.get("/status")
async def get_robot_status():
    """Get current robot status"""
    global controller
    
    if not controller:
        raise HTTPException(status_code=500, detail="Controller not initialized")
    
    status = controller.get_status()
    
    return {
        "robot": status,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/labware")
async def get_labware_registry():
    """Get all loaded labware"""
    global controller
    
    if not controller:
        raise HTTPException(status_code=500, detail="Controller not initialized")
    
    labware = controller.get_labware_registry()
    
    return {
        "labware": labware,
        "count": len(labware),
        "timestamp": datetime.now().isoformat()
    }


@app.post("/robot/home")
async def home_robot():
    """Home robot axes"""
    global controller
    
    if not controller:
        raise HTTPException(status_code=500, detail="Controller not initialized")
    
    result = controller.home_robot()
    
    return {
        "operation": result,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/robot/lights")
async def control_lights(on: bool = True):
    """Control robot lights"""
    global controller
    
    if not controller:
        raise HTTPException(status_code=500, detail="Controller not initialized")
    
    result = controller.set_lights(on)
    
    return {
        "operation": result,
        "timestamp": datetime.now().isoformat()
    }


# Utility functions
async def save_execution_results(request: ExecutionRequest, execution_result: Dict[str, Any]):
    """Save execution results to file"""
    try:
        # Create results directory if it doesn't exist
        results_dir = "execution_results"
        os.makedirs(results_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"execution_{timestamp}.json"
        filepath = os.path.join(results_dir, filename)
        
        # Prepare data to save
        save_data = {
            "request": {
                "workflow": {
                    "nodes": [node.dict() for node in request.workflow.nodes],
                    "metadata": request.workflow.metadata
                },
                "config": request.config.dict()
            },
            "execution_result": execution_result,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save to file
        with open(filepath, 'w') as f:
            json.dump(save_data, f, indent=2)
        
        logging.info(f"Execution results saved to {filepath}")
        
    except Exception as e:
        logging.error(f"Failed to save execution results: {str(e)}")


async def save_execution_results_canvas(request: CanvasExecutionRequest, execution_result: Dict[str, Any]):
    """Save Canvas execution results to file"""
    try:
        # Create results directory if it doesn't exist
        results_dir = "execution_results"
        os.makedirs(results_dir, exist_ok=True)
        
        # Generate filename with workflow name and timestamp
        workflow_name = request.canvas_workflow.metadata.get("name", "unnamed")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"canvas_{workflow_name}_{timestamp}.json"
        filepath = os.path.join(results_dir, filename)
        
        # Prepare data to save
        save_data = {
            "request": {
                "canvas_workflow": request.canvas_workflow.dict(),
                "config": request.config.dict()
            },
            "execution_result": execution_result,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save to file
        with open(filepath, 'w') as f:
            json.dump(save_data, f, indent=2)
        
        logging.info(f"Canvas execution results saved to {filepath}")

    except Exception as e:
        logging.error(f"Failed to save Canvas execution results: {str(e)}")


@app.get("/managers")
async def get_available_managers():
    """Get information about available workflow managers"""
    try:
        managers = WorkflowManagerFactory.get_available_managers()
        return {
            "managers": managers,
            "current_manager": current_manager_type,
            "prefect_available": PREFECT_AVAILABLE
        }
    except Exception as e:
        logging.error(f"Failed to get managers: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to get managers",
                "message": str(e)
            }
        )


@app.post("/managers/configure")
async def configure_manager(config: ManagerConfig):
    """Configure the workflow manager"""
    global controller, mapper, current_manager_type, deployment_manager

    try:
        # Initialize controller if needed
        if not controller:
            controller = OpentronsController(
                dry_run=config.dry_run,
                robot_ip=config.robot_ip
            )

        # Create the appropriate manager
        if config.manager_type == "native":
            mapper = WorkflowMapper(controller)
            current_manager_type = "native"
            deployment_manager = None

        elif config.manager_type == "prefect":
            if not PREFECT_AVAILABLE:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Prefect not available",
                        "message": "Install Prefect with: pip install prefect>=2.10.0"
                    }
                )

            mapper = WorkflowManagerFactory.create_manager(
                WorkflowManagerType.PREFECT, controller
            )
            current_manager_type = "prefect"
            deployment_manager = PrefectDeploymentManager(controller)

        else:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid manager type",
                    "message": f"Unknown manager type: {config.manager_type}"
                }
            )

        logging.info(f"Configured workflow manager: {config.manager_type}")

        return {
            "status": "success",
            "manager_type": current_manager_type,
            "message": f"Workflow manager configured: {config.manager_type}"
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Manager configuration failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Manager configuration failed",
                "message": str(e)
            }
        )


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logging.error(f"Unhandled exception: {str(exc)}")
    return HTTPException(
        status_code=500,
        detail={
            "error": "Internal server error",
            "message": str(exc)
        }
    )


if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )