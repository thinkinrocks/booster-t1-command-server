import logging
import asyncio
from abc import ABC, abstractmethod
import os


class RobotCommander(ABC):
    @abstractmethod
    def busy(self) -> bool:
        pass

    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    async def wave_hand(self, parameters: dict = {}):
        pass

    @abstractmethod
    def cancel_wave_hand(self):
        pass

    @abstractmethod
    async def move_forward(self, parameters: dict = {}):
        pass

    @abstractmethod
    async def move_backward(self, parameters: dict = {}):
        pass

    @abstractmethod
    async def turn_left(self, parameters: dict = {}):
        pass

    @abstractmethod
    async def turn_right(self, parameters: dict = {}):
        pass


class MockRobotCommander(RobotCommander):
    def __init__(self, verbose: bool = False):
        self.logger = logging.getLogger("mock-robot-commander")
        self.logger.setLevel(logging.DEBUG if verbose else logging.INFO)
        self.logger.info("Initializing mock robot commander")

        self.command_queue = asyncio.Queue(maxsize=1)
        self.busy_lock = asyncio.Lock()

    def busy(self) -> bool:
        return self.busy_lock.locked()

    def name(self) -> str:
        return "mock"

    async def _process_next_command(self):
        """Process the next command from the queue if available."""
        if not self.command_queue.empty():
            self.logger.debug("Executing next command from queue")
            try:
                command, params = self.command_queue.get_nowait()
                await command(params)
            except asyncio.QueueEmpty:
                self.logger.debug("Command queue is empty, skipping command")

    async def _execute_wave_hand(self, parameters: dict = {}):
        """Internal method that executes wave_hand with the busy_lock."""
        async with self.busy_lock:
            self.logger.debug("Waving hand")
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

    async def _execute_move_forward(self, parameters: dict = {}):
        """Internal method that executes move_forward with the busy_lock."""
        async with self.busy_lock:
            self.logger.debug("Moving forward")
            await asyncio.sleep(1)
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
            await asyncio.sleep(1)
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
            await asyncio.sleep(1)
        await self._process_next_command()

    async def turn_left(self):
        """Non-blocking turn_left command - runs in background."""
        if self.busy():
            self.logger.debug("Robot is busy, adding command to queue")
            try:
                self.command_queue.put_nowait((self._execute_turn_left, 1))
            except asyncio.QueueFull:
                self.logger.debug("Command queue is full, skipping command")
            return

        # Start the command execution in the background
        asyncio.create_task(self._execute_turn_left(1))

    async def _execute_turn_right(self, parameters: dict = {}):
        """Internal method that executes turn_right with the busy_lock."""
        async with self.busy_lock:
            self.logger.debug("Turning right")
            await asyncio.sleep(1)
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


class RobotCommanderFactory:
    def __init__(self, verbose: bool = False):
        self.logger = logging.getLogger("robot-commander-factory")
        self.verbose = verbose
        self.robot_commander = None

    def using_booster_t1(self) -> "RobotCommanderFactory":
        from robot_commander.booster_t1_robot import BoosterT1Commander

        self.logger.info("Using booster_t1 robot commander")
        if self.robot_commander is None or not isinstance(
            self.robot_commander, BoosterT1Commander
        ):
            self.robot_commander = BoosterT1Commander(verbose=self.verbose)
        return self

    def using_mock(self) -> "RobotCommanderFactory":
        self.logger.info("Using mock robot commander")
        if self.robot_commander is None or not isinstance(
            self.robot_commander, MockRobotCommander
        ):
            self.robot_commander = MockRobotCommander(verbose=self.verbose)
        return self

    def get_robot_commander(self) -> RobotCommander:
        if self.robot_commander is not None:
            return self.robot_commander
        elif os.getenv("ROBOT") == "booster-t1":
            return self.using_booster_t1().robot_commander
        else:
            return self.using_mock().robot_commander


robot_commander_factory = RobotCommanderFactory(verbose=True)


def robot_commander() -> RobotCommander:
    return robot_commander_factory.get_robot_commander()
