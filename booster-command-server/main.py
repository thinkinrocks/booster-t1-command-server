import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Annotated, Optional, Dict, Any, List
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
    title="Booster T1 Robot Command API",
    description="""
# Booster T1 Robot Command Server

This API provides control interface for the Booster T1 humanoid robot platform.

## Features

- **Movement Control**: Move the robot forward, backward, and turn left/right
- **Hand Gestures**: Control hand waving actions
- **Command Queueing**: Automatic command queueing when robot is busy
- **Status Monitoring**: Health check and status endpoints

## Robot Specifications

The Booster T1 is a humanoid robot with the following capabilities:
- Locomotion: Forward/backward movement and rotation
- Hand control: Wave gestures with open/close actions
- Speed control: Configurable movement speeds (default: 0.5 m/s forward, 0.2 m/s backward, 0.2 rad/s rotation)

## Command Queue

The robot processes one command at a time. If the robot is busy executing a command, 
new commands will be queued (max queue size: 1). If the queue is full, additional 
commands will be skipped.

## Usage Notes

- All movement commands execute for 1 second by default
- The `wave-hand` command duration can be customized via the `duration` parameter
- The robot automatically stops movement after command completion
    """,
    version="1.0.0",
    contact={
        "name": "Booster Platform Support",
        "url": "https://github.com/thinkinrocks/booster-platform",
    },
    license_info={
        "name": "License",
        "url": "https://github.com/thinkinrocks/booster-platform/blob/main/LICENSE",
    },
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)


# ============================================================================
# Pydantic Models
# ============================================================================

class CommandResponse(BaseModel):
    """Standard response model for all command endpoints"""
    
    success: bool = Field(..., description="Whether the command was successfully queued/executed")
    message: str = Field(..., description="Human-readable status message")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional response data (if applicable)")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Command executed successfully",
                "data": None,
            }
        }


class WaveHandRequest(BaseModel):
    """Request parameters for wave hand command"""
    
    duration: float = Field(
        default=1.0,
        ge=0.1,
        le=10.0,
        description="Duration in seconds to keep hand waving (default: 1.0 seconds)",
        examples=[1.0, 2.5, 5.0]
    )

    class Config:
        json_schema_extra = {
            "example": {
                "duration": 1.0
            }
        }


class RobotStatus(BaseModel):
    """Robot status information"""
    
    robot_name: str = Field(..., description="Name/type of the robot commander")
    is_busy: bool = Field(..., description="Whether the robot is currently executing a command")
    
    class Config:
        json_schema_extra = {
            "example": {
                "robot_name": "booster_t1",
                "is_busy": False
            }
        }


class CommandInfo(BaseModel):
    """Information about an available command"""
    
    command: str = Field(..., description="Command name")
    description: str = Field(..., description="Command description")
    parameters: Optional[Dict[str, str]] = Field(None, description="Available parameters and their descriptions")


class CommandsListResponse(BaseModel):
    """List of available commands"""
    
    commands: List[CommandInfo] = Field(..., description="Available robot commands")
    
    class Config:
        json_schema_extra = {
            "example": {
                "commands": [
                    {
                        "command": "wave-hand",
                        "description": "Make the robot wave its hand",
                        "parameters": {"duration": "Duration in seconds (0.1-10.0)"}
                    },
                    {
                        "command": "move-forward",
                        "description": "Move the robot forward",
                        "parameters": None
                    }
                ]
            }
        }


# ============================================================================
# API Endpoints
# ============================================================================

@app.get(
    "/",
    summary="API Information",
    description="Get basic information about the Booster T1 Robot Command API",
    tags=["General"]
)
async def root():
    """
    Welcome endpoint providing API overview and available endpoints.
    """
    return {
        "message": "Welcome to Booster T1 Robot Command API",
        "version": "1.0.0",
        "documentation": "/docs",
        "openapi_spec": "/openapi.json",
        "endpoints": {
            "/health": "Health check",
            "/status": "Robot status",
            "/commands": "List available commands",
            "/wave-hand": "Wave hand gesture",
            "/cancel-wave-hand": "Cancel wave hand",
            "/move-forward": "Move forward",
            "/move-backward": "Move backward",
            "/turn-left": "Turn left",
            "/turn-right": "Turn right",
        },
    }


@app.get(
    "/health",
    summary="Health Check",
    description="Check if the API server is running and healthy",
    tags=["General"]
)
async def health_check():
    """
    Simple health check endpoint to verify the server is operational.
    
    Returns:
        dict: Status indicating the server is healthy
    """
    return {"status": "healthy"}


@app.get(
    "/status",
    response_model=RobotStatus,
    summary="Get Robot Status",
    description="Get the current status of the robot, including type and busy state",
    tags=["General"]
)
async def get_status(
    robot_cmd: Annotated[RobotCommander, Depends(robot_commander)],
):
    """
    Retrieve the current status of the robot.
    
    Returns:
        RobotStatus: Information about robot type and current busy state
    """
    return RobotStatus(
        robot_name=robot_cmd.name(),
        is_busy=robot_cmd.busy()
    )


@app.get(
    "/commands",
    response_model=CommandsListResponse,
    summary="List Available Commands",
    description="Get a list of all available robot commands with descriptions",
    tags=["General"]
)
async def list_commands():
    """
    List all available commands that can be executed on the robot.
    
    Returns:
        CommandsListResponse: List of commands with descriptions and parameters
    """
    commands = [
        CommandInfo(
            command="wave-hand",
            description="Make the robot wave its hand (opens hand, waits for duration, then closes)",
            parameters={"duration": "Duration in seconds to keep hand waving (0.1-10.0, default: 1.0)"}
        ),
        CommandInfo(
            command="cancel-wave-hand",
            description="Immediately close the hand and cancel any ongoing wave gesture",
            parameters=None
        ),
        CommandInfo(
            command="move-forward",
            description="Move the robot forward at 0.5 m/s for 1 second",
            parameters=None
        ),
        CommandInfo(
            command="move-backward",
            description="Move the robot backward at 0.2 m/s for 1 second",
            parameters=None
        ),
        CommandInfo(
            command="turn-left",
            description="Rotate the robot left at 0.2 rad/s for 1 second",
            parameters=None
        ),
        CommandInfo(
            command="turn-right",
            description="Rotate the robot right at 0.2 rad/s for 1 second",
            parameters=None
        ),
    ]
    return CommandsListResponse(commands=commands)


@app.post(
    "/wave-hand",
    response_model=CommandResponse,
    summary="Wave Hand",
    description="Command the robot to wave its hand for a specified duration",
    tags=["Hand Gestures"],
    responses={
        200: {
            "description": "Command successfully queued or executed",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Waving hand",
                        "data": None
                    }
                }
            }
        }
    }
)
async def wave_hand(
    request: WaveHandRequest = WaveHandRequest(),
    robot_cmd: Annotated[RobotCommander, Depends(robot_commander)] = None,
):
    """
    Make the robot wave its hand.
    
    The robot will:
    1. Open its hand
    2. Keep the hand open for the specified duration
    3. Close the hand
    
    If the robot is busy, the command will be queued (queue size: 1).
    If the queue is full, the command will be skipped.
    
    **Technical Details:**
    - Uses B1HandAction.kHandOpen to open the hand
    - Uses B1HandAction.kHandClose to close the hand
    - Default duration: 1.0 second
    - Min duration: 0.1 seconds
    - Max duration: 10.0 seconds
    """
    await robot_cmd.wave_hand(parameters={"duration": request.duration})
    return CommandResponse(
        success=True,
        message=f"Waving hand for {request.duration} seconds",
        data=None
    )


@app.post(
    "/cancel-wave-hand",
    response_model=CommandResponse,
    summary="Cancel Wave Hand",
    description="Immediately cancel the wave hand gesture and close the hand",
    tags=["Hand Gestures"],
    responses={
        200: {
            "description": "Hand gesture cancelled",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Cancelled wave hand",
                        "data": None
                    }
                }
            }
        }
    }
)
async def cancel_wave_hand(
    robot_cmd: Annotated[RobotCommander, Depends(robot_commander)],
):
    """
    Immediately close the hand and cancel any ongoing wave gesture.
    
    This command:
    - Closes the hand immediately using B1HandAction.kHandClose
    - Can be used to interrupt a wave gesture in progress
    - Executes synchronously (does not use the command queue)
    """
    robot_cmd.cancel_wave_hand()
    return CommandResponse(
        success=True,
        message="Cancelled wave hand",
        data=None
    )


@app.post(
    "/move-forward",
    response_model=CommandResponse,
    summary="Move Forward",
    description="Move the robot forward for 1 second",
    tags=["Movement"],
    responses={
        200: {
            "description": "Movement command queued or executed",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Moving forward",
                        "data": None
                    }
                }
            }
        }
    }
)
async def move_forward(
    robot_cmd: Annotated[RobotCommander, Depends(robot_commander)],
):
    """
    Move the robot forward.
    
    **Movement Parameters:**
    - Speed: 0.5 m/s
    - Duration: 1 second
    - Direction: Straight forward (no lateral or rotational movement)
    
    **Technical Details:**
    - Uses robot_client.Move(0.5, 0.0, 0.0)
    - Linear velocity: 0.5 m/s forward
    - Lateral velocity: 0.0 m/s
    - Angular velocity: 0.0 rad/s
    - Automatically stops after 1 second
    
    If the robot is busy, the command will be queued.
    """
    await robot_cmd.move_forward(parameters={})
    return CommandResponse(
        success=True,
        message="Moving forward",
        data=None
    )


@app.post(
    "/move-backward",
    response_model=CommandResponse,
    summary="Move Backward",
    description="Move the robot backward for 1 second",
    tags=["Movement"],
    responses={
        200: {
            "description": "Movement command queued or executed",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Moving backward",
                        "data": None
                    }
                }
            }
        }
    }
)
async def move_backward(
    robot_cmd: Annotated[RobotCommander, Depends(robot_commander)],
):
    """
    Move the robot backward.
    
    **Movement Parameters:**
    - Speed: 0.2 m/s (slower than forward for safety)
    - Duration: 1 second
    - Direction: Straight backward (no lateral or rotational movement)
    
    **Technical Details:**
    - Uses robot_client.Move(-0.2, 0.0, 0.0)
    - Linear velocity: -0.2 m/s (negative = backward)
    - Lateral velocity: 0.0 m/s
    - Angular velocity: 0.0 rad/s
    - Automatically stops after 1 second
    
    If the robot is busy, the command will be queued.
    """
    await robot_cmd.move_backward(parameters={})
    return CommandResponse(
        success=True,
        message="Moving backward",
        data=None
    )


@app.post(
    "/turn-left",
    response_model=CommandResponse,
    summary="Turn Left",
    description="Rotate the robot left (counter-clockwise) for 1 second",
    tags=["Movement"],
    responses={
        200: {
            "description": "Turn command queued or executed",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Turning left",
                        "data": None
                    }
                }
            }
        }
    }
)
async def turn_left(
    robot_cmd: Annotated[RobotCommander, Depends(robot_commander)],
):
    """
    Rotate the robot left (counter-clockwise).
    
    **Rotation Parameters:**
    - Angular velocity: 0.2 rad/s counter-clockwise
    - Duration: 1 second
    - Total rotation: ~11.5 degrees
    
    **Technical Details:**
    - Uses robot_client.Move(0.0, 0.0, 0.2)
    - Linear velocity: 0.0 m/s
    - Lateral velocity: 0.0 m/s
    - Angular velocity: 0.2 rad/s (positive = counter-clockwise)
    - Automatically stops after 1 second
    
    If the robot is busy, the command will be queued.
    """
    await robot_cmd.turn_left(parameters={})
    return CommandResponse(
        success=True,
        message="Turning left",
        data=None
    )


@app.post(
    "/turn-right",
    response_model=CommandResponse,
    summary="Turn Right",
    description="Rotate the robot right (clockwise) for 1 second",
    tags=["Movement"],
    responses={
        200: {
            "description": "Turn command queued or executed",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Turning right",
                        "data": None
                    }
                }
            }
        }
    }
)
async def turn_right(
    robot_cmd: Annotated[RobotCommander, Depends(robot_commander)],
):
    """
    Rotate the robot right (clockwise).
    
    **Rotation Parameters:**
    - Angular velocity: 0.2 rad/s clockwise
    - Duration: 1 second
    - Total rotation: ~11.5 degrees
    
    **Technical Details:**
    - Uses robot_client.Move(0.0, 0.0, -0.2)
    - Linear velocity: 0.0 m/s
    - Lateral velocity: 0.0 m/s
    - Angular velocity: -0.2 rad/s (negative = clockwise)
    - Automatically stops after 1 second
    
    If the robot is busy, the command will be queued.
    """
    await robot_cmd.turn_right(parameters={})
    return CommandResponse(
        success=True,
        message="Turning right",
        data=None
    )


if __name__ == "__main__":
    if os.getenv("ROBOT") == "booster-t1":
        robot_commander_factory.using_booster_t1()
    else:
        robot_commander_factory.using_mock()
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
