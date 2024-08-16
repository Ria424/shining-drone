from time import sleep, time

from CodingRider.drone import DataType, DeviceType, Drone, State

from util import println

_battery: int = 0
_drone: Drone
_log: bool = False

def _state_callback(state: State):
    global _battery
    _battery = state.battery

def get_battery(interval: float = 0, timeout: float = 0.5) -> int:
    global _battery, _drone, _log

    start_time = time()

    _battery = -1
    _drone.sendRequest(DeviceType.Drone, DataType.State)
    while _battery < 0 and ((time_took := time() - start_time) < timeout):
        sleep(interval)

    if time_took >= timeout:
        if _log:
            println("Battery - retrying...")
        return get_battery(interval, timeout)
    return _battery

def init_battery(drone: Drone, flag_log=False):
    global _battery, _drone, _log
    _drone = drone
    _log = flag_log
    _drone.setEventHandler(DataType.State, _state_callback)