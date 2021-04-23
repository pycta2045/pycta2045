import serial
from serial.tools.list_ports import comports

class COM:
    def __init__(self, port="/dev/ttyS6"):
        self.port = port
        self.verify_port()
        return
    def verify_port(self):
        ports = list(comports())
        print(ports)
        return self.port in ports
    def get_next(self):
        
        return
        