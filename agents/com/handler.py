import serial
from serial.tools.list_ports import comports
from serial.tools.list_ports_linux import SysFS
import glob
# import io



class COM:
    '''
        Note: This module is not well-tested due to missing equipments for now. 
    '''
    def __init__(self, port="/dev/ttyS6"):
        self.port = port
        ports = list(serial.tools.list_ports.comports())
        ports = list(map(lambda x: x.name,ports))
        if not self.port in ports:
            raise Exception(f"port {self.port} not found")
        try:
            self.ser = serial.Serial(self.port)
            self.sio = io.TextIOWrapper(io.BufferedRWPair(self.ser,self.ser))
            print('sucess',self.ser,sell.sio)
        except Exception as e:
            print(e)
        return
    def send(self,data):
        print('wrote= ',self.sio.write(f'{data}\n'))
        self.sio.flush()  
        return
    def recv(self):
        data = self.ser.readline()
        return data.decode()
        
