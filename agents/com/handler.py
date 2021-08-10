import serial
from serial.tools.list_ports import comports #from serial.tools.list_ports_linux import SysFS
from multiprocessing import Process, Lock, Queue
import time, pandas as pd, traceback as tb
from agents.cta2045.handler import UnsupportedCommandException

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
    def __init__(self, checksum, transform, is_valid, port="/dev/ttyS6",timeout=.4,verbose=False):
        '''
            * Note:
                * timeout (defualt) is set to 500 ms as specified by CTA2045
        '''
        self.port = port
        ports = list(serial.tools.list_ports.comports())
        ports = list(map(lambda x: x.name,ports))
        port = self.port
        self.ser = None
        if 'dev' in self.port:
            port = self.port.split('/')[-1]
        if not port in ports:
            raise Exception(f"port {self.port} not found")
        try:
            self.ser = serial.Serial(self.port)
            self.send_delay = .08 # (send delay) 40 ms of MAX time after receiving a msg and BEFORE sending ack/nak (200 ms according to CTA2045)
            self.recv_delay = .1 # (recv delay) 100 ms of MIN time after tansmission until the start of another (according to CTA2045)
            self.sleep_until = 1 # should be 100 mS of delay between recveing & sending a message (refer to CTA2045 msg sync info on t_MA & t_IM)
            #self.ser.rs485_mode = serial.rs485.RS485Settings(delay_before_tx=tma,delay_before_rx=tim)
            self.ser.baudrate=19200 # according to CTA2045
            self.ser.timeout=timeout
            #self.ser.delay_before_tx = self.tma
            #self.ser.delay_before_rx = self.tim
            self.checksum: callable = checksum # function type
            self.transform: callable = transform # function type
            self.is_valid_cta: callable = is_valid # function type
            self.ser.bytesize= serial.EIGHTBITS
            self.buffer = Queue()
            self.lock = Lock()
            self.process = None
            self.stopped = True
            self.last_msg_timestamp =  0
            print('comport was created sucessfully')
            self.__msgs = pd.DataFrame(columns = ['time','src','dest','message'])
            self.verbose = verbose

        except Exception as e:
            print(e)
            exit()
        return
    def __del__(self):
        self.stopped = True
        return
    def send(self,data):
        packet = bytearray()
        self.__log({'src':self.US,'dest':self.THEM,'message':data})
        data = list(map(lambda x:int(x,16),data.split(' ')))
        packet.extend(data)
        if time.time() - self.last_msg_timestamp < self.sleep_until:
            time.sleep(self.send_delay) # delay until you can send the next msg
        res = self.ser.write(packet)
        self.last_msg_timestamp = time.time()
        self.sleep_until = time.time() + self.recv_delay
        return res>=2
    def __recv(self):
        '''
            TODO
        '''
        data = None
        buff = []
        print('starting listener...')
        try:
            while True:
                if time.time() - self.last_msg_timestamp < self.sleep_until:
                    time.sleep(self.recv_delay)
                if self.ser.inWaiting() > 0:
                    data = self.ser.read(self.ser.inWaiting())
                    data = list(map(lambda x: self.transform(int(hex(x),16)),data))
                    # iterate over bytes in data and append each one onto the buffer
                    # each time you append to the buffer, check if that completes a cta2045 command
                    for i in data:
                        buff.append(i)
                        try:
                            if self.is_valid_cta(buff):
                                buff = " ".join(buff)
                                self.buffer.put((buff,time.time())) # this is thread-safe queue -- no need to acquire lock
                                if self.verbose:
                                    print('BUFFER SIZE: ',self.buffer.qsize())
                                self.last_msg_time_timestamp = time.time()
                                self.sleep_until = time.time() + self.send_delay # send delay
                                # log
                                self.__log({'src':self.THEM,'dest':self.US,'message':buff})
                                buff = []
                        except UnsupportedCommandException as e:
                            continue
                if self.stopped:
                    print('exiting...')
                    break
        except Exception as e:
            print(tb.format_tb(e))

        return
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
    def start(self):
        '''
            Purpose: starts listen on the given port. It creates a process with __recv running in it.
            Args: None
            Returns: None
            NOTES:
                * After facing behavior problems introduced by the use of threading and GIL, I decided to go with multiprocessing instead.
                * This is a workaround dealing with GIL

        '''
        if self.process == None and self.ser != None:
            self.process = Process(target=self.__recv)
            self.process.daemon = True
            # flush the buffers
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            self.stopped = False
            self.process.start() # starts a new thread to listen to packets
        return
    def get_next_msg(self):
        '''
            blocking function that returns the next msg in the buffer
        '''
        msg = None
        msg = self.buffer.get() # no need to acquire -- blocks by default
            #if t >= time.time() + self.ser.timeout:
                #raise TimeoutException("waiting for ack/nak timout!")
        return msg
    def dump_log(self,fname):
        if fname != None:
            self.__msgs.to_csv(fname)
            return True
        return False
