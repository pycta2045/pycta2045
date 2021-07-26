import serial
from serial.tools.list_ports import comports #from serial.tools.list_ports_linux import SysFS
import serial.rs485
import time
import io



class COM:
    '''
        Note: This module is not well-tested due to missing equipments for now.
    '''
    def __init__(self, checksum, transform, port="/dev/ttyS6",timeout=.02):
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
            self.tma = .2 # 200 ms of MAX time after receiving a msg and BEFORE sending ack/nak (200 ms according to CTA2045)
            self.tim = .1 # 100 ms of MIN time after tansmission until the start of another (according to CTA2045)
            #self.ser.rs485_mode = serial.rs485.RS485Settings(delay_before_tx=tma,delay_before_rx=tim)
            self.ser.baudrate=19200 # according to CTA2045
            #self.sio = io.TextIOWrapper(io.BufferedRWPair(self.ser,self.ser))
            self.ser.timeout=timeout
            self.ser.delay_before_tx = self.tma
            self.ser.delay_before_rx = self.tim
            self.checksum: callable = checksum # function type
            self.transform: callable = transform # function type
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
        #print('wrote= ',packet)
        #time.sleep(self.tim)
        return res>=2

    def recv(self):
        '''
            This function takes a
        '''
        buff = data = None
        while True:
            if self.ser.inWaiting()>0:
                buff = self.ser.read(self.ser.inWaiting())
                data = list(map(lambda x: self.transform(int(hex(x),16)),buff))
                if len(data) > 2:
                    unchecked_data = data[:-2]
                    checked_data = self.checksum(" ".join(unchecked_data)).split(" ")
                    #print("unchecked: ",unchecked_data)
                    #print("checked: ",checked_data)
                    #print("orig:",data)
                    if data == checked_data:
                        return " ".join(data)
                else:
                    return " ".join(data)
            #time.sleep(self.ser.timeout)


        return buff

