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
        if not self.verify_port():
            raise Exception(f"port {self.port} not found")
        # TODO: handle errors
        self.ser = serial.Serial(self.port)
        self.sio = io.TextIOWrapper(io.BufferedRWPair(self.ser,self.ser))
        return
    def verify_port(self,links=False):  
        # credit comports: https://github.com/pyserial/pyserial/blob/master/serial/tools/list_ports_linux.py
        devices = glob.glob('/dev/ttyS*')           # built-in serial ports
        devices.extend(glob.glob('/dev/ttyUSB*'))   # usb-serial with own driver
        devices.extend(glob.glob('/dev/ttyXRUSB*')) # xr-usb-serial port exar (DELL Edge 3001)
        devices.extend(glob.glob('/dev/ttyACM*'))   # usb-serial with CDC-ACM profile
        devices.extend(glob.glob('/dev/ttyAMA*'))   # ARM internal port (raspi)
        devices.extend(glob.glob('/dev/rfcomm*'))   # BT serial devices
        devices.extend(glob.glob('/dev/ttyAP*'))    # Advantech multi-port serial controllers
        if links:
            devices.extend(list_ports_common.list_links(devices))
        return [info
                for info in [SysFS(d) for d in devices]
                if info.subsystem != "platform"]    # hide non-present internal serial ports
        # ports = list(map(lambda x: x[0],comports()))  
        return self.port in ports
    def send(self,data):
        print('wrote= ',self.sio.write(f'{data}\n'))
        self.sio.flush()  
        return
    def recv(self):
        data = self.ser.readline()
        return data.decode()
        