from pycta2045.cta2045 import *
from pycta2045.com import *
import sys, os, pandas as pd, time,  select, traceback as tb
from pycta2045.models import *
from queue import Queue
from datetime import datetime as dt
from threading import Thread
import wiringpi # used to provide a custom logging in WH station



choices = {
    1:"shed",
    2:"endshed",
    3:"loadup",
    4:"critical peak event",
    5:"grid emergency",
    6:"operating status request",
    7:"device info request",
    8:"commodity read request",
    9:"quit"
}
class UnknownModeException(Exception):
    def __init__(self,msg):
        self.msg = msg
        super().__init__(self.msg)
        return

class CTA2045Device:
    def __init__(self,mode:str='DCM',timeout:int=2,model=None,comport:str='/dev/ttyS6',verbose:bool=False):
        self.mode = mode.upper()
        self.model = model
        self.log = Queue()
        self.complete_log = pd.DataFrame()
        self.cta_mod = CTA2045()
        self.com = COM(mode=mode,transform=self.cta_mod.hexify,is_valid=self.cta_mod.is_valid,port=comport,verbose=verbose)
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
        self.thread = None
        self.running = False
        self.block = False
        self.last_beat = 1
        self.FDT = {}
        self.row = []
        # initialize wiringpi
        wiringpi.mcp3004Setup(100,0) # channel 100

        return

    def __heartbeat(self):
        '''
            The purpose of this function is to send heartbeat when the time is right
        '''
        now = time.time()
        # check if a minute has passed & mode is DCM (only DCMs send heartbeats)
        if self.mode == 'DCM' and (now - self.last_beat) >= 60: # 60 secs == 1 min
            self.send('outside comm connection status')
            self.send('commodity read request')
            self.send('operating status request')
            self.last_beat = now # record time
    def __del__(self):
        try:
            self.stop()
        except:
            pass
        return
    def __dump_file(self):
        ts = dt.fromtimestamp(int(float(self.row[0])))
        d = self.row[1]
        actual_power = (wiringpi.analogRead(100) / 1023) * 4.4 # 4.4 is reference voltage
        actual_power *= 2400 # 240 (volts) scaled by 10
        cr = ''
        cr += f"\t{d['cumulative_amount0']},\t{d['instantaneous_rate0']},"
        cr += f"\t{d['cumulative_amount1']},\t{d['cumulative_amount2']}"
        op = self.row[2]['op_state_code']
        row = f"{ts},{cr},\t{round(actual_power,3)},\t{op}\n"
        with open('log.csv','a') as f:
            f.write(row)
        return

    def __update_log(self,msg:str)->None:
        if 'read response' in msg:
            self.row.append(msg.split('\t')[0])
            self.row.append(eval(msg.split('\t')[-1]))
        elif 'status response' in msg and len(self.row) == 2:
            self.row.append(eval(msg.split('\t')[-1]))
            # dump into file
            self.__dump_file()
            self.row = [] # reset list
        self.last_log_msg = msg
        self.log.put(msg)
        return
    def get_log(self)->pd.DataFrame:
        ts = []
        msgs = []
        args = []
        while not self.log.empty():
            e = self.log.get().split('\t')
            ts.append(e[0])
            msgs.append(e[1])
            args.append(e[2])
        df = pd.DataFrame({'time':ts, 'event':msgs,'arguments':args})
        df.set_index('time',inplace=True)
        self.complete_log = self.complete_log.append(df)
        return self.complete_log.copy()
    def __write(self,msg:str,log:bool=False,end:str='\n')->None:
        if log:
            self.__update_log(msg)
        if self.block:
            print(msg,end=end)
        return
    def __recv(self,verbose:bool=True)->dict:
        res = None
        try:
            res = self.com.get_next_msg()
            if res != None:
                msg,t = res # check against timeout
                if time.time() - t >= self.timeout:
                    self.__update_log(f"{t}\twaiting for response timeout!\t")
                    raise TimeoutException('Timeout!')
                res = self.cta_mod.from_cta(msg)
                if type(res) == dict:
                    self.__write(f"{t}\treceived {res['command']}\t{res['args']}",log=True)
                    if verbose:
                        for k,v in res['args'].items():
                            self.__write(f"\t{k} = {v}")
                if 'op1' in res and res['op1']!='none':
                    self.last_command = res['op1']
        except UnsupportedCommandException as e:
            self.__write(f"{t}\treceived Unsupported Command -- {e.message}\t",log=True)
            raise UnsupportedCommandException(msg) # propagate exception
        except UnknownCommandException as e:
            self.__write(f"{t}\treceived Unknwon command -- {msg}\t",log=True)
            raise UnknownCommandException(msg) # propagate exception
        return res
    def send(self,cmd:str,args:dict={},verbose:bool=False)->bool:
        if not self.running:
            raise Exception('device not running. Try the run() function first!')
        ret = False
        c = self.cta_mod.to_cta(cmd,args=args)
        self.com.send(c)
        self.__write(f'{time.time()}\tsent {cmd}\t{args}',log=True)
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
    def __setup(self)->bool:
        res = None
        success=False
        cmds = [('intermediate mtsq','intermediate'),
                ('data-link mtsq','data-link'),
                ('max payload request','max payload'),
                ('basic mtsq','basic')
                ]
        # heart beat before anything
        self.__heartbeat()
        for cmd,flag in cmds:
            try:
                if self.send(cmd):
                    # wait for response
                    res = self.__recv()
                if res != None and 'command' in res and res['command'] == 'ack':
                    self.support_flags[flag] = True
                if 'max' in cmd:
                    res = self.__recv() # capture max payload
                    if res != None and 'args' in res and 'max' in res['command']:
                        length = res['args']['max_payload_length']
                        self.support_flags[flag] = int(length)
            except TimeoutException:
                flag = False
            except UnsupportedCommandException  as e:
                pass
        self.__write(str(self.support_flags))
        success = self.support_flags['intermediate'] and self.support_flags['data-link'] and self.support_flags['max payload'] > 0
        return success
    def __prompt(self,valid:bool=False)->None:
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
    def __run_dcm(self)->None:
        valid = True
        # sent unsupported commands -- doesn't make sense for DCM to ack any of them
        self.cta_mod.set_supported('shed',False)
        self.cta_mod.set_supported('endshed',False)
        self.cta_mod.set_supported('loadup',False)
        self.cta_mod.set_supported('grid emergency',False)
        self.cta_mod.set_supported('critical peak event',False)
        self.cta_mod.set_supported('commodity read request',False)
        choice = ''
        last_sz = self.log.qsize()
        self.__prompt(valid)
        while not self.stopped:
            if last_sz+2 <= self.log.qsize(): # if log has changed by 2 msgs
                time.sleep(.2*self.timeout) # sleep to allow log msgs to be printed
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
                self.stop()
                return
            elif choice != '':
                self.send(choice) # sent command, daemon receives and responds to the command
                choice = ''
            valid = True
        return
    # ------------------------- Daemon Loop ----------------------------------
    # -----------------------------------------------------------------------------
    def __run_daemon(self)->None:
        while not self.stopped:
            self.__heartbeat()
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
                self.send('app nak',{'app_nak_reason':'opcode not supported'})
            except KeyboardInterrupt as e:
                break # exit loop & return
        return
    def run(self,block:bool=False)->None:
        self.com.start()
        self.running = True
        self.block = block
        self.__setup()
        # run daemon
        self.thread = Thread(target=self.__run_daemon)
        self.thread.daemon = True
        self.stopped = False
        self.thread.start()

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
            if block:
                # Bring the daemon to the "foreground"
                self.thread.join()
        elif self.mode=='DCM':
            # sent unsupported commands -- doesn't make sense for DCM to ack any of them
            self.cta_mod.set_supported('shed',False)
            self.cta_mod.set_supported('endshed',False)
            self.cta_mod.set_supported('loadup',False)
            self.cta_mod.set_supported('grid emergency',False)
            self.cta_mod.set_supported('critical peak event',False)
            self.cta_mod.set_supported('device info request',False)
            self.cta_mod.set_supported('commodity read request',False)
            if block:
                # The receiver should be running as a daemon
                self.__run_dcm()
        else:
            raise UnknownModeException(f'Unknown Mode: {self.mode}')
        return
    def stop(self)->None:
        if not self.stopped:
            self.com.stop()
            self.stopped = True
            if self.thread != None:
                self.thread.join()
        return
