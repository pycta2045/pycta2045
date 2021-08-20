from pycta2045.cta2045 import *
from pycta2045.com import *
import sys, os, pandas as pd, time,  select, traceback as tb, multiprocessing#, import threading
from pycta2045.models import *
from queue import Queue
from datetime import datetime as dt
from threading import Thread



choices = {
    1:"shed",
    2:"endshed",
    3:"loadup",
    4: "critical peak event",
    5:"grid emergency",
    6:"operating status request",
    7:"device info request",
    8:"quit"
}

class UnknownModeException(Exception):
    def __init__(self,msg):
        self.msg = msg
        super().__init__(self.msg)
        return

recv_color = 'red'
send_color = 'green'

class CTA2045Device:
    def __init__(self,mode='DCM',timeout=1,model=None,comport='/dev/ttyS6',verbose=False):
        self.mode = mode.upper()
        self.model = model
        self.log = multiprocessing.Queue()
        self.cta_mod = CTA2045()
        self.com = COM(checksum=self.cta_mod.checksum,transform=self.cta_mod.hexify,is_valid=self.cta_mod.is_valid,port=comport,verbose=verbose)
        self.last_command = '0x00'
        # flags for minimum cta2045 support
        self.support_flags = {
            'intermediate':False,
            'data-link':False,
            'basic':False,
            'max payload':0
        }
        self.timeout = timeout
        return
    def __update_log(self,msg):
        self.log.put(msg)
        return
    def get_log(self):
        ts = []
        msgs = []
        while not self.log.empty():
            t,msg = self.log.get().split(':')
            ts.append(t)
            msgs.append(msg)
        df = pd.DataFrame({'time':ts, 'event':msgs})
        # df.set_index('time',inplace=True)
        return df
    def __write(self,msg,log=False,end='\n'):
        if log:
            self.__update_log(msg)
        print(msg,end=end)
        return
    def __update_log(self,msg,log=False,end='\n'):
        if log:
            self.__update_log(msg)
        # print(msg,end=end)
        return
    def __recv(self,verbose=True):
        res = None
        try:
            res = self.com.get_next_msg()
            if res != None:
                msg,t = res # check against timeout
                if time.time() - t >= self.timeout:
                    self.__update_log(f"{t}: waiting for response timeout!",log=True)
                    raise TimeoutException('Timeout!')
                res = self.cta_mod.from_cta(msg)
                if type(res) == dict:
                    self.__write(f"{t}: received {res['command']}",log=True)
                    if verbose:
                        for k,v in res['args'].items():
                            self.__write(f"\t{k} = {v}")
                if 'op1' in res:
                    self.last_command = res['op1']
        except UnsupportedCommandException as e:
            self.__write(f"{t}: received Unsupported Command -- {e.message}",log=True)
            raise UnsupportedCommandException(msg) # propagate exception
        except UnknownCommandException as e:
            self.__write(f"{t}: received Unknwon command -- {msg}",log=True)
            raise UnknownCommandException(msg) # propagate exception
        return res
    def __send(self,cmd,args={},verbose=False):
        ret = False
        c = self.cta_mod.to_cta(cmd,args=args)
        self.com.send(c)
        self.__write(f'{time.time()}: sent {cmd}',log=True)
        if verbose:
            if len(args) > 0:
                self.__write('\twith args:')
                for k,v in args.items():
                    if not v[0].isalpha():
                        v = v.replace(' 0x','')
                        v = int(v,16)
                    self.__write(f'\t{k}: {v}')
        ret = True # else an exception would be raised and this statement would be skipped when unwinding the stack
        return ret
    def __setup(self):
        res = None
        success=False
        cmds = [('intermediate mtsq','intermediate'),
                ('data-link mtsq','data-link'),
                ('max payload request','max payload'),
                ('basic mtsq','basic')
                ]
        for cmd,flag in cmds:
            try:
                #cmd = 'intermediate mtsq'
                if self.__send(cmd):
                    # wait for response
                    res = self.__recv()
                if res != None and 'command' in res and res['command'] == 'ack':
                    self.support_flags[flag] = True
                if 'max' in cmd:
                    res = self.__recv() # capture max payload
                    if res != None and 'args' in res and 'max' in res['command']:
                        self.__send('ack')
                        length = res['args']['max_payload_length']
                        self.support_flags[flag] = int(length)
            except TimeoutException:
                flag = False
            except UnsupportedCommandException  as e:
                pass
        self.__write(str(self.support_flags))
        success = self.support_flags['intermediate'] and self.support_flags['data-link'] and self.support_flags['max payload'] > 0
        return success
    def __prompt(self,valid=False):
        '''
            outputs a prompt message to the screen

        '''
        if not valid:
            self.__write(f"{'-'*5}> INVALID. Try again!\n")
            self.prompted = False
        msg = "select a command:\n"
        for k,v in choices.items():
            msg += f"{k}: {v}\n"
        self.__write(msg)
        self.__write("enter a choice: ")
        return
    # ------------------------- DCM Loop ----------------------------------
    # -----------------------------------------------------------------------------
    def __run_dcm(self):
        valid = True
        
        # sent unsupported commands -- doesn't make sense for DCM to ack any of them
        self.cta_mod.set_supported('shed',False)
        self.cta_mod.set_supported('endshed',False)
        self.cta_mod.set_supported('loadup',False)
        self.cta_mod.set_supported('grid emergency',False)
        self.cta_mod.set_supported('critical peak event',False)
        # run daemon
        proc = multiprocessing.Process(target=self.__run_daemon)
        proc.daemon = True
        proc.start()
        choice = ''
        # prompt_time = 30 # every 30 secs will prompt
        # next_prompt = time.time() + prompt_time
        last_sz = self.log.qsize()
        self.__prompt(valid)
        while 1:
            if last_sz+2 <= self.log.qsize(): # if log has changed by 2 msgs
                time.sleep(.5*self.timeout) # sleep to allow log msgs to be printed
                self.__prompt(valid)
                last_sz = self.log.qsize() # update last_log size
            i = select.select([sys.stdin],[],[],0) # 0=> disables blocking mode
            if i[0]:
                try:
                    choice = sys.stdin.read(1) # read 1 char
                    sys.stdin.flush()
                    choice = int(choice) # try to cast it
                    valid = choice in choices
                    choice = '' if not valid else choices[choice]
                except (KeyError,ValueError) as e:
                    valid = False
                    self.__prompt(valid)
                    choice = ''
                    continue
            if choice == 'quit':
                proc.terminate()
                return
            elif choice != '':
                self.__send(choice) # sent command, daemon receives and responds to the command
                choice = ''
            valid = True
        return
    # ------------------------- Daemon Loop ----------------------------------
    # -----------------------------------------------------------------------------
    def __run_daemon(self):
        while 1:
            args = {}
            try:
                res = self.__recv() # always waiting for commands
                if res != None:
                    cmd = res['command']
                    # invoke model with request command -- if supported
                    if cmd in self.FDT:
                        args = res['args']
                        args = self.FDT[cmd](payload=args)
                    complement = self.cta_mod.complement(cmd)
                    for cmd in complement:
                        if cmd == 'app ack':
                            self.__send(cmd, {'last_opcode':self.last_command})
                        elif cmd == 'nak':
                            self.__send(cmd,{'nak_reason':'unsupported'})
                        else:
                            self.__send(cmd,args)
            except TimeoutException as e:
                # nothing was received from UCM
                pass
            except (UnsupportedCommandException,UnknownCommandException) as e:
                self.__send('nak',{'nak_reason':'unsupported'})
            except KeyboardInterrupt as e:
                break # exit loop & return
        return
    def run(self):
        self.com.start()
        self.__setup()
        if self.mode == 'DER':
            # validate model in DER mode
            assert(isinstance(self.model,CTA2045Model))
            self.FDT = {
                'shed':self.model.shed,
                'endshed':self.model.endshed,
                'loadup':self.model.loadup,
                'operating status request':self.model.operating_status,
                'commodity read request':self.model.commodity_read,
                'grid emergency':self.model.grid_emergency,
                'critical peak event':self.model.critical_peak_event
            }
            self.__run_daemon()
        elif self.mode=='DCM':
            self.FDT = {} # empty it
            self.__run_dcm()
        else:
            raise UnknownModeException(f'Unknown Mode: {self.mode}')
        return self.get_log()

# ============================= Simplified inteface of CTA2045Device ==================================
class SimpleCTA2045Device:
    '''
        This class provides a simplified interface for pycta2045.
        One can use it to send CTA2045 commands via the send method. 
        One can also get a log of the messages exchanged via the get_log method.
        It allows the user to just send a command without writing the logic of what and
        what not to send next (the part of recieving and responding to basic acks/naks, etc. is automated). 
    '''
    def __init__(self,mode='DCM',timeout=1.,model=None,comport='/dev/ttyS6'):
        self.mode = mode.upper()
        self.model = model
        self.log = Queue()
        self.cta_mod = CTA2045()
        self.com = COM(checksum=self.cta_mod.checksum,transform=self.cta_mod.hexify,is_valid=self.cta_mod.is_valid,port=comport)
        self.last_command = '0x00'
        # flags for minimum cta2045 support
        self.support_flags = {
            'intermediate':False,
            'data-link':False,
            'basic':False,
            'max payload':0
        }
        self.timeout = timeout
        self.last_log_msg = None
        self.stopped = True
        return
    def __update_log(self,msg):
        self.last_log_msg = msg
        self.log.put(msg)
        return
    def get_log(self):
        ts = []
        msgs = []
        while not self.log.empty():
            t,msg = self.log.get().split(':')
            ts.append(dt.fromtimestamp(round(float(t),3)))
            msgs.append(msg)
        df = pd.DataFrame({'time':ts, 'event':msgs})
        df.set_index('time',inplace=True)
        return df
    def __recv(self,verbose=True):
        res = None
        try:
            res = self.com.get_next_msg()
            if res != None:
                msg,t = res # check against timeout
                t = t
                # if time.time() - t >= self.timeout:
                #     self.__update_log(f"{t}: waiting for response timeout!")
                #     raise TimeoutException('Timeout!')
                res = self.cta_mod.from_cta(msg)
                if type(res) == dict:
                    self.__update_log(f"{t}: received {res['command']}")
                if 'op1' in res:
                    self.last_command = res['op1']
        except UnsupportedCommandException as e:
            self.__update_log(f"{t}: received Unsupported Command -- {e.message}")
            raise UnsupportedCommandException(msg) # propagate exception
        except UnknownCommandException as e:
            self.__update_log(f"{t}: received Unknwon command -- {msg}")
            raise UnknownCommandException(msg) # propagate exception
        except TimeoutException as e:
            t = time.time()
            if not 'timeout' in self.last_log_msg:
                self.__update_log(f"{t}: waiting for message timeout -- {e.message}")
            raise TimeoutException(e.message) # propagate exception
        return res
    def send(self,cmd,args={},verbose=False):
        ret = False
        c = self.cta_mod.to_cta(cmd,args=args)
        ret = self.com.send(c)
        self.__update_log(f'{time.time()}: sent {cmd}')
        return ret
    def __setup(self):
        res = None
        success=False
        cmds = [('intermediate mtsq','intermediate'),
                ('data-link mtsq','data-link'),
                ('max payload request','max payload'),
                ('basic mtsq','basic')
                ]
        for cmd,flag in cmds:
            try:
                #cmd = 'intermediate mtsq'
                if self.send(cmd):
                    # wait for response
                    res = self.__recv()
                if res != None and 'command' in res and res['command'] == 'ack':
                    self.support_flags[flag] = True
                if 'max' in cmd:
                    res = self.__recv() # capture max payload
                    if res != None and 'args' in res and 'max' in res['command']:
                        self.send('ack')
                        length = res['args']['max_payload_length']
                        self.support_flags[flag] = int(length)
            except TimeoutException:
                flag = False
            except UnsupportedCommandException  as e:
                pass
        success = self.support_flags['intermediate'] and self.support_flags['data-link'] and self.support_flags['max payload'] > 0
        return success
    # ------------------------- Daemon Loop ----------------------------------
    # -----------------------------------------------------------------------------
    def __run_daemon(self):
        while not self.stopped:
            args = {}
            try:
                res = self.__recv() # always waiting for commands
                if res != None:
                    cmd = res['command']
                    # invoke model with request command -- if supported
                    if cmd in self.FDT:
                        args = res['args']
                        args = self.FDT[cmd](payload=args)
                    complement = self.cta_mod.complement(cmd)
                    for cmd in complement:
                        if cmd == 'app ack':
                            self.send(cmd, {'last_opcode':self.last_command})
                        elif cmd == 'nak':
                            self.send(cmd,{'nak_reason':'unsupported'})
                        else:
                            self.send(cmd,args)
            except TimeoutException as e:
                # nothing was received from UCM
                pass
            except (UnsupportedCommandException,UnknownCommandException) as e:
                self.send('nak',{'nak_reason':'unsupported'})
            except KeyboardInterrupt as e:
                return # exit loop & return
        return
    def run(self):
        self.com.start()
        self.__setup()
        if self.mode == 'DER':
            # validate model in DER mode
            assert(isinstance(self.model,CTA2045Model))
            self.FDT = {
                'shed':self.model.shed,
                'endshed':self.model.endshed,
                'loadup':self.model.loadup,
                'operating status request':self.model.operating_status,
                'commodity read request':self.model.commodity_read,
                'grid emergency':self.model.grid_emergency,
                'critical peak event':self.model.critical_peak_event
            }
        elif self.mode=='DCM':
            self.FDT = {} # empty it
            # sent unsupported commands -- doesn't make sense for DCM to ack any of them
            self.cta_mod.set_supported('shed',False)
            self.cta_mod.set_supported('endshed',False)
            self.cta_mod.set_supported('loadup',False)
            self.cta_mod.set_supported('grid emergency',False)
            self.cta_mod.set_supported('critical peak event',False)
        else:
            raise UnknownModeException(f'Unknown Mode: {self.mode}')
        # run daemon
        self.thread = Thread(target=self.__run_daemon)
        self.thread.daemon = True
        self.stopped = False
        self.thread.start()
        return
    def stop(self):
        self.com.stop()
        self.stopped = True
        self.thread.join()
        return
