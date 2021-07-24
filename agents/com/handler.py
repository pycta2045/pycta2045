import serial
from serial.tools.list_ports import comports
#from serial.tools.list_ports_linux import SysFS
import serial.rs485
import io



class COM:
    '''
        Note: This module is not well-tested due to missing equipments for now.
    '''
    def __init__(self, port="/dev/ttyS6",timeout=2):
        '''
            * Note:
                * timeout (defualt) is set to 500 ms as specified by CTA2045
        '''
        self.port = port
        ports = list(serial.tools.list_ports.comports())
        ports = list(map(lambda x: x.name,ports))
        port = self.port
        if 'dev' in self.port:
            port = self.port.split('/')[-1]
        if not port in ports:
            raise Exception(f"port {self.port} not found")
        try:
            self.ser = serial.Serial(self.port)
            tma = .2 # 200 ms of MAX time after receiving a msg and BEFORE sending ack/nak (200 ms according to CTA2045)
            tim = .1 # 100 ms of MIN time after tansmission until the start of another (according to CTA2045)
            self.ser.rs485_mode = serial.rs485.RS485Settings(delay_before_tx=tma,delay_before_rx=tim)
            self.ser.baudrate=19200 # according to CTA2045
            #self.sio = io.TextIOWrapper(io.BufferedRWPair(self.ser,self.ser))
            self.ser.timeout=timeout
            self.ser.bytesize= serial.EIGHTBITS
            print('comport was created sucessfully')
        except Exception as e:
            print(e)
        return
    def send(self,data):
        packet = bytearray()
        data = list(map(lambda x:int(x,16),data.split(' ')))
        packet.extend(data)
        res = self.ser.write(packet)
        print('wrote= ',packet)
        return res>=2
    def recv(self,length=4096):
        buff = ''
        #data = self.ser.read()
        #ret = self.ser.
        buff = data

        return data

