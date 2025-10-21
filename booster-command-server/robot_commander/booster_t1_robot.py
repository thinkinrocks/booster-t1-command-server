import asyncio
import logging
from booster_robotics_sdk_python import (
    B1HandAction,
    B1LocoClient,
    ChannelFactory,
)

from robot_commander import RobotCommander


class BoosterT1Commander(RobotCommander):
    def __init__(self, network_interface: str = "127.0.0.1", verbose: bool = False):
        self.logger = logging.getLogger("booster-t1-commander")
        self.logger.setLevel(logging.DEBUG if verbose else logging.INFO)
        self.logger.info(f"Initializing robot client with host: {network_interface}")
        ChannelFactory.Instance().Init(0, network_interface)
        self.robot_client = B1LocoClient()
        self.robot_client.Init()
        self.busy_lock = asyncio.Lock()
        self.command_queue = asyncio.Queue(maxsize=1)

    def busy(self) -> bool:
        return self.busy_lock.locked()

    async def _process_next_command(self):
        """Process the next command from the queue if available."""
        if not self.command_queue.empty():
            self.logger.debug("Executing next command from queue")
            try:
                command, parameters = self.command_queue.get_nowait()
                await command(parameters)
            except asyncio.QueueEmpty:
                self.logger.debug("Command queue is empty, skipping command")

    async def _execute_wave_hand(self, parameters: dict = {}):
        """Internal method that executes wave_hand with the busy_lock."""
        async with self.busy_lock:
            self.logger.debug("Waving hand")
            self.robot_client.WaveHand(B1HandAction.kHandOpen)
            await asyncio.sleep(parameters.get("duration", 1))
            self.cancel_wave_hand()
            self.logger.debug("Waved hand")
        await self._process_next_command()

    async def wave_hand(self, parameters: dict = {}):
        """Non-blocking wave_hand command - runs in background."""
        if self.busy():
            self.logger.debug("Robot is busy, adding command to queue")
            try:
                self.command_queue.put_nowait((self._execute_wave_hand, parameters))
            except asyncio.QueueFull:
                self.logger.debug("Command queue is full, skipping command")
            return

        # Start the command execution in the background
        asyncio.create_task(self._execute_wave_hand(parameters))

    def cancel_wave_hand(self):
        self.logger.debug("Cancelling waved hand")
        self.robot_client.WaveHand(B1HandAction.kHandClose)

    def _cancel_move(self):
        self.logger.debug("Cancelling move")
        self.robot_client.Move(0.0, 0.0, 0.0)

    async def _execute_move_forward(self, parameters: dict = {}):
        """Internal method that executes move_forward with the busy_lock."""
        async with self.busy_lock:
            self.logger.debug("Moving forward")
            self.robot_client.Move(0.5, 0.0, 0.0)
            await asyncio.sleep(1)
            self._cancel_move()
            self.logger.debug("Moved forward")
        await self._process_next_command()

    async def move_forward(self, parameters: dict = {}):
        """Non-blocking move_forward command - runs in background."""
        if self.busy():
            self.logger.debug("Robot is busy, adding command to queue")
            try:
                self.command_queue.put_nowait((self._execute_move_forward, parameters))
            except asyncio.QueueFull:
                self.logger.debug("Command queue is full, skipping command")
            return

        # Start the command execution in the background
        asyncio.create_task(self._execute_move_forward(parameters))

    async def _execute_move_backward(self, parameters: dict = {}):
        """Internal method that executes move_backward with the busy_lock."""
        async with self.busy_lock:
            self.logger.debug("Moving backward")
            self.robot_client.Move(-0.2, 0.0, 0.0)
            await asyncio.sleep(1)
            self._cancel_move()
            self.logger.debug("Moved backward")
        await self._process_next_command()

    async def move_backward(self, parameters: dict = {}):
        """Non-blocking move_backward command - runs in background."""
        if self.busy():
            self.logger.debug("Robot is busy, adding command to queue")
            try:
                self.command_queue.put_nowait((self._execute_move_backward, parameters))
            except asyncio.QueueFull:
                self.logger.debug("Command queue is full, skipping command")
            return

        # Start the command execution in the background
        asyncio.create_task(self._execute_move_backward(parameters))

    async def _execute_turn_left(self, parameters: dict = {}):
        """Internal method that executes turn_left with the busy_lock."""
        async with self.busy_lock:
            self.logger.debug("Turning left")
            self.robot_client.Turn(0.0, 0.0, 0.2)
            await asyncio.sleep(1)
            self._cancel_move()
            self.logger.debug("Turned left")
        await self._process_next_command()

    async def turn_left(self, parameters: dict = {}):
        """Non-blocking turn_left command - runs in background."""
        if self.busy():
            self.logger.debug("Robot is busy, adding command to queue")
            try:
                self.command_queue.put_nowait((self._execute_turn_left, parameters))
            except asyncio.QueueFull:
                self.logger.debug("Command queue is full, skipping command")
            return

        # Start the command execution in the background
        asyncio.create_task(self._execute_turn_left(parameters))

    async def _execute_turn_right(self, parameters: dict = {}):
        """Internal method that executes turn_right with the busy_lock."""
        async with self.busy_lock:
            self.logger.debug("Turning right")
            self.robot_client.Turn(0.0, 0.0, -0.2)
            await asyncio.sleep(1)
            self._cancel_move()
            self.logger.debug("Turned right")
        await self._process_next_command()

    async def turn_right(self, parameters: dict = {}):
        """Non-blocking turn_right command - runs in background."""
        if self.busy():
            self.logger.debug("Robot is busy, adding command to queue")
            try:
                self.command_queue.put_nowait((self._execute_turn_right, parameters))
            except asyncio.QueueFull:
                self.logger.debug("Command queue is full, skipping command")
            return

        # Start the command execution in the background
        asyncio.create_task(self._execute_turn_right(parameters))
