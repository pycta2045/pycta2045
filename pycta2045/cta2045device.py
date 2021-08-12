from pycta2045.cta2045 import *
from pycta2045.com import *
import sys, os, time,  select, traceback as tb, multiprocessing#, import threading
from pycta2045.models import *


choices = {
    1:"shed",
    2:"endshed",
    3:"loadup",
    4: "critical peak event",
    5:"grid emergency",
    6:"operating status request",
    7:"quit"
}

class DCM:
    pass
class DER:
    pass
class UnknownModeException(Exception):
    def __init__(self,msg):
        self.msg = msg
        super().__init__(self.msg)
        return


class CTA2045Device:
    def __init__(self,mode=DCM,log_size=10,model=None,comport='/dev/ttyS6'):
        self.mode = mode.__name__
        self.model = model
        self.log = []
        self.log_sz = log_size if log_size > 0 else -(log_size-1)
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
        self.timeout = .4
        return
    def __update_log(self,msg):
        self.log.append(msg)
        self.log = self.log[-self.log_sz:]
        return
    def __write(self,msg,log=False,clear=False,end='\n'):
        sz = 0
        #with self.lock:
            #sz=self.terminal.write("".join(self.log))
            #sz+=self.terminal.write(msg)
        if clear == True:
            print("\n".join(self.log))
            print('-'*20)
        else:
            print(msg,end=end)
        if log:
                self.__update_log(msg)
        return
    def __clear(self):
        os.system('clear')
        self.__write('',clear=True)
        return
    def __recv(self,verbose=True):
        res = None
        try:
            res = self.com.get_next_msg()
            if res != None:
                t_e = time.time()
                msg,t = res # check against timeout
                if time.time() - t >= self.timeout:
                    self.__write(f"<-== waiting for response timeout!",log=True)
                    raise TimeoutException('Timeout!')
                res = self.cta_mod.from_cta(msg)
                if type(res) == dict:
                    self.__write(f"<-== received: {res['command']}",log=True)
                    if verbose:
                        for k,v in res['args'].items():
                            self.__write(f"\t{k} = {v}")
                if 'op1' in res:
                    self.last_command = res['op1']
        except UnsupportedCommandException as e:
            self.__write(f"<-== Unsupported command received: {e.message}",log=True)
            raise UnsupportedCommandException(msg) # propagate exception
        except UnsupportedCommandException as e:
            self.__write(f"<-== Unknwon command received: {msg}",log=True)
            raise UnsupportedCommandException(msg) # propagate exception
        return res
    def __send(self,cmd,args={},verbose=False):
        ret = False
        c = self.cta_mod.to_cta(cmd,args=args)
        self.com.send(c)
        self.__write(f'==-> sent {cmd}',log=True)
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
        while 1:
            # self.__clear()
            self.__prompt(valid)
            if select.select([sys.stdin],[],[],0): # 0=> disables blocking mode
                try:
                    choice = sys.stdin.read(1) # read 1 char
                    choice = int(choice) # try to cast it
                    valid = choice in choices
                    choice = '' if not valid else choices[choice]
                except (KeyError,ValueError) as e:
                    valid = False
                    choice = ''
                    continue
            if choice == 'quit':
                proc.terminate()
                return
            elif choice != '':
                self.__send(choice) # sent command, daemon receives and responds to the command
            valid = True
            self.__write(f"==========***** VALID: {valid}")
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
                pass
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
        return