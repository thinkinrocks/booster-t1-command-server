import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Annotated, Optional, Dict, Any
import uvicorn
import logging

from robot_commander import (
    RobotCommander,
    robot_commander,
    robot_commander_factory,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # Console output
        logging.FileHandler("server.log"),  # File output
    ],
)

logging.getLogger("watchfiles.main").setLevel(logging.WARNING)

app = FastAPI(
    title="Booster Platform API",
    description="A FastAPI server for processing commands",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)


class CommandRequest(BaseModel):
    """Request model for commands"""

    command: str
    parameters: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "command": "example_command",
                "parameters": {"param1": "value1", "param2": "value2"},
            }
        }


class CommandResponse(BaseModel):
    """Response model for commands"""

    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Command executed successfully",
                "data": {"result": "example_result"},
            }
        }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Booster Platform API",
        "endpoints": {
            "/command": "POST - Execute commands",
            "/docs": "GET - API documentation",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/command", response_model=CommandResponse)
async def execute_command(
    request: CommandRequest,
    robot_commander: Annotated[RobotCommander, Depends(robot_commander)],
):
    """
    Execute a command based on the request

    Args:
        request: CommandRequest containing the command name and parameters
        robot_client: B1LocoClient instance injected as dependency

    Returns:
        CommandResponse with execution results
    """

    command = request.command
    parameters = request.parameters or {}

    # Example command routing structure (to be implemented)
    if command == "ping":
        return CommandResponse(success=True, message="Pong!", data={"echo": parameters})
    if command == "wave-hand":
        await robot_commander.wave_hand(parameters=parameters)
        return CommandResponse(success=True, message="Waving hand", data=None)
    if command == "cancel-wave-hand":
        robot_commander.cancel_wave_hand()
        return CommandResponse(success=True, message="Cancelled waved hand", data=None)
    if command == "move-forward":
        await robot_commander.move_forward(parameters=parameters)
        return CommandResponse(success=True, message="Moving forward", data=None)
    if command == "move-backward":
        await robot_commander.move_backward(parameters=parameters)
        return CommandResponse(success=True, message="Moving backward", data=None)
    if command == "turn-left":
        await robot_commander.turn_left(parameters=parameters)
        return CommandResponse(success=True, message="Turning left", data=None)
    if command == "turn-right":
        await robot_commander.turn_right(parameters=parameters)
        return CommandResponse(success=True, message="Turning right", data=None)

    # Unknown command
    return CommandResponse(
        success=False, message=f"Unknown command: {command}", data=None
    )


if __name__ == "__main__":
    if os.getenv("ROBOT") == "booster-t1":
        robot_commander_factory.using_booster_t1()
    else:
        robot_commander_factory.using_mock()
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
