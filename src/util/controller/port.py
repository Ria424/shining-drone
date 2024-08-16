from serial.tools.list_ports import comports
from serial.tools.list_ports_common import ListPortInfo

from src.error import ControllerNotFound

def is_controller_port(port_info: ListPortInfo):
    return port_info.description.find("CH340") != -1

def get_controller_ports():
    return filter(is_controller_port, comports())

def get_controller_port_name(index: int):
    controller_ports = tuple(get_controller_ports())
    if not controller_ports:
        raise ControllerNotFound("Controller not found.")

    return controller_ports[index].name