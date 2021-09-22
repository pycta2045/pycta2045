import serial
from serial.tools.list_ports import comports
from threading import Thread, Lock
import time, pandas as pd, traceback as tb, numpy as np
from pycta2045.cta2045 import UnsupportedCommandException, UnknownCommandException
from queue import Queue, Empty

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
    def __init__(self, checksum:callable, transform:callable, is_valid:callable, mode:str='DER', port:str="/dev/ttyS6",timeout:float=.4,verbose:bool=False):
        '''
            Constructor
            * Note:
                * checksum: a callabe variable (function) that checks whether or not the received message is complete.
                * transform: a callable variable (function) that transforms the received message into the desired format.
                * is_valid: a callable variable (function) that checks if the received message is valid.
                * mode: desired mode of operation (used mostly for logging) -- DER vs UCM operating mode.
                * port: com port used to listen on.
                * timeout (defualt) is set to 500 ms as specified by CTA2045.
                * verbose: bool to print out notable events.
        '''
        self.port = port
        self.ser = None
        self.ser = serial.Serial(self.port)
        self.send_delay = .04 # (send delay) 40 ms of MAX time after receiving a msg and BEFORE sending ack/nak (200 ms according to CTA2045)
        self.recv_delay = .1 # (recv delay) 100 ms of MIN time after tansmission until the start of another (according to CTA2045)
        self.sleep_until = 1 # should be 100 mS of delay between recveing & sending a message (refer to CTA2045 msg sync info on t_MA & t_IM)
        self.ser.baudrate=19200 # according to CTA2045
        self.ser.timeout=timeout
        self.checksum: callable = checksum # function type
        self.transform: callable = transform # function type
        self.is_valid_cta: callable = is_valid # function type
        self.ser.bytesize= serial.EIGHTBITS
        self.buffer = Queue()
        self.lock = Lock()
        self.thread = None
        self.stopped = True
        self.last_msg_timestamp =  0
        if verbose:
            print('comport was created sucessfully')
        self.__msgs = pd.DataFrame(columns = ['time','src','dest','message'])
        self.msg_expected = False
        self.verbose = verbose
        if mode == 'DCM': self.US,self.THEM = ('DCM','DER') # reverse default mode
        return
    def __del__(self):
        '''
            Destructor that ensures all threads have safely exited. 
        '''
        self.stopped=True
        return
    def send(self,data:str)->bool:
        '''
            Member method that translates the passed data into bytearray before sending it through the COM port. 
        '''
        packet = bytearray()
        self.__log({'src':self.US,'dest':self.THEM,'message':data})
        data = list(map(lambda x:int(x,16),data.split(' ')))
        if len(data) > 4:
            self.msg_expected = True
        packet.extend(data)
        if time.time() - self.last_msg_timestamp < self.sleep_until:
            time.sleep(self.send_delay) # delay until you can send the next msg
        res = self.ser.write(packet)
        self.last_msg_timestamp = time.time()
        self.sleep_until = time.time() + self.recv_delay
        return res>=2
    def __recv(self)->None:
        '''
            Private function that (blockingly) waits for messages from the COM port.
            It uses a buffer (a queue) shared by all threads
        '''
        data = None
        buff = np.array([]) # local buffer used to process chunk of packages
        if self.verbose:
            print('starting listener...')
        # clear buffer
        self.ser.flushInput()
        self.ser.flushOutput()
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
                        buff = np.append(buff,i)
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
                                buff = np.array([])
                        except UnknownCommandException as e:
                            continue                    
                    if self.msg_expected:
                        self.msg_expected = False
                if self.stopped:
                    print('exiting...')
                    break
        except Exception as e:
            print(tb.format_tb(e))

        return
    def __log(self,context:dict)->None:
        '''
            Purpose: Logs input messages and outputs it into a file
            Args: message (dict) contains:
                * src: source of the message
                * dest: destination of the message
                * message: content of the message
            Return: void
        '''
        t = time.time()
        self.__msgs=self.__msgs.append({'time':t,'src': context['src'],'dest':context['dest'],'message':context['message']},ignore_index=True)
        if self.verbose == True:
            st = '<'*5 if context['dest'] == self.US else '>'*5
            print(f"{t}:{st} FROM: {context['src']} TO: {context['dest']} MESSAGE: {context['message']}")
        self.last_message = context['message']
        return
    def start(self)->None:
        '''
            Purpose: starts listen on the given port. It creates a thread with __recv running in it.
            Args: None
            Returns: None
        '''
        if self.thread == None and self.ser != None:
            self.thread = Thread(target=self.__recv)
            self.thread.daemon = True
            # flush the buffers
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            self.stopped = False
            self.thread.start() # starts a new thread to listen to packets
        return
    def get_next_msg(self)->str:
        '''
            Non-blocking function that returns the next msg in the buffer. 
            If buffer is empty, it waits until timeout value before raising timeout exception.
        '''
        msg = None
        try:
            msg = self.buffer.get(timeout=self.ser.timeout) # no need to acquire -- blocks by default
        except Empty as e:
            if self.msg_expected:
                raise TimeoutException("Timout!")
        return msg
    def write_log(self,fname:str)->bool:
        '''
            Memeber method that takes in the name of a file and writes the log as a CSV using the passed name. 
            If a path is desired, include that as part of `fname`.
        '''
        if fname != None:
            self.__msgs.to_csv(fname)
            return True
        return False
    def get_log(self)->pd.DataFrame:
        '''
            Member method that dumps the log log of messages (incoming & outgoing) through the port 
        '''
        return self.__msgs
    def stop(self)->None:
        '''
            Member method that terminates the running threat safely. Upon invoking it, it joins the listening threat (blocks until the thread has exited).  
        '''
        self.stopped = True
        if not self.thread == None:
            self.thread.join()
        if self.verbose: 
            print('stopped com!')
        return
