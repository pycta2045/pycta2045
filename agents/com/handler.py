import serial
from serial.tools.list_ports import comports #from serial.tools.list_ports_linux import SysFS
# import serial.rs485
import time
import pandas as pd

class TimeoutException(Exception):
    '''
        This class is used to indicate waiting for a response from the other device has timed out.
    '''
    def __init__(self,msg="waiting for ack/nak"):
        self.message = msg
        super().__init__(self.message)

class COM:
    '''
        Note: This module is not well-tested due to missing equipments for now.
    '''
    US = 'DER'
    THEM = 'DCM'
    def __init__(self, checksum, transform, port="/dev/ttyS6",timeout=.02,verbose=False):
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
            self.ser.timeout=timeout
            self.ser.delay_before_tx = self.tma
            self.ser.delay_before_rx = self.tim
            self.checksum: callable = checksum # function type
            self.transform: callable = transform # function type
            self.ser.bytesize= serial.EIGHTBITS
            print('comport was created sucessfully')
            self.__msgs = pd.DataFrame(columns = ['time','src','dest','message'])
            self.verbose = verbose
        except Exception as e:
            print(e)
        return
    def send(self,data):
        packet = bytearray()
        self.__log({'src':self.US,'dest':self.THEM,'message':data})
        data = list(map(lambda x:int(x,16),data.split(' ')))
        packet.extend(data)
        res = self.ser.write(packet)
        time.sleep(self.tim)
        return res>=2
    def recv(self):
        '''
            TODO
        '''
        data = None
        timeout = time.time()+self.ser.timeout
        while True:
            if self.ser.inWaiting()>0:
                data = self.ser.read(self.ser.inWaiting())
                data = list(map(lambda x: self.transform(int(hex(x),16)),data))
                time.sleep(self.tim)
                if len(data) > 2:
                    unchecked_data = data[:-2]
                    checked_data = self.checksum(" ".join(unchecked_data)).split(" ")
                    if data == checked_data:
                        data = " ".join(data)
                else:
                    data = " ".join(data)
                # log
                self.__log({'src':self.THEM,'dest':self.US,'message':data})
                return data
            if time.time() >= timeout:
                raise TimeoutException("waiting for ack/nak timeout!")
        return data
    def __log(self,context):
        '''
            Purpose: Logs input messages and outputs it into a file
            Args: message (dict) contains:
                * src: source of the message
                * dest: destination of the message
                * message: content of the message
            Return: void
        '''
        self.__msgs=self.__msgs.append({'time':int(time.time()),'src': context['src'],'dest':context['dest'],'message':context['message']},ignore_index=True)
        if self.verbose == True:
            st = '<'*5 if context['dest'] == self.US else '>'*5
            print(f"{st} FROM: {context['src']} TO: {context['dest']} MESSAGE: {context['message']}")
        return
    def dump_log(self,fname):
        if fname != None:
            self.__msgs.to_csv(fname)
            return True
        return False
