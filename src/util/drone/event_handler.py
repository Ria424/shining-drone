from time import sleep, time
from typing import Any, Callable

from CodingRider.drone import DataType, DeviceType, Drone

from util import println

class DroneEventHandler:
    def __init__(self, drone: Drone, log=False):
        self.drone = drone
        self._log = log
        self._callbacks: dict[DataType, Callable[[Any], None]] = {}
        self._check_variables: dict[DataType, Any] = {}

        self._battery: int = 0

    def bind_event(self, data_type: DataType, callback: Callable[[Any], None]):
        def check(v: Any):
            self._check_variables[data_type] = v

        self._callbacks[data_type] = callback
        self.drone.setEventHandler(data_type, check)

    def unbind_event(self, data_type: DataType):
        self.drone._eventHandler.d.pop(data_type)
        self._callbacks.pop(data_type)

    def send_request(self, device_type: DeviceType, data_type: DataType, interval: float = 0, timeout: float = 0.5):
        self._check_variables.pop(data_type, None)

        start_time = time()

        self.drone.sendRequest(device_type, data_type)
        while data_type not in self._check_variables and ((time_took := time() - start_time) < timeout):
            sleep(interval)

        if time_took >= timeout:
            if self._log:
                println("DroneEventHandler - Retrying...")
            self._check_variables[data_type] = None
            self.send_request(device_type, data_type, interval, timeout)
        else:
            self._callbacks[data_type](self._check_variables[data_type])