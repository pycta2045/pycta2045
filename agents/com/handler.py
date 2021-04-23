import serial
from serial.tools.list_ports import comports
import io

class COM:
    def __init__(self, port="/dev/ttyS6"):
        self.port = port
        if not self.verify_port():
            raise Exception(f"port {self.port} not found")
        # TODO: handle errors
        self.ser = serial.Serial(self.port)
        self.sio = io.TextIOWrapper(io.BufferedRWPair(self.ser,self.ser))
        return
    def verify_port(self):
        ports = list(map(lambda x: x[0],comports()))
        return self.port in ports
    def send(self,data):
        print('wrote= ',self.sio.write(f'{data}\n'))
        self.sio.flush()  
        return
    def recv(self):
        data = self.ser.readline()
        return data.decode()
        