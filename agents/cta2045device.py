from cta2045 import CTA2045
from com import COM,TimeoutException
import sys, os, traceback as tb, abc#, import threading
from multiprocessing import Process
from models import model as AbstractModel


choices = {
    1:"shed",
    2:"endshed",
    3:"loadup",
    4:"operating status request",
    5:"quit"
}

class DCM:
    pass
class DER:
    pass
class UnknownModeException(Exception):
    def __init__(self,msg):
        self.msg = msg
        super().__init__(self.msg)
        pass



class CTA2045Device:
    def __init__(self,mode=DCM,log_size=10,model=None):
        self.mode = mode.__name__
        self.model = model
        self.log = []
        self.log_sz = log_size if log_size > 0 else -(log_size-1)
        #self.terminal = sys.stdout
        #self.screen_sz = 0
        #self.lock = threading.Lock()
        self.cta_mod = CTA2045()
        self.com = COM(checksum=self.cta_mod.checksum,transform=self.cta_mod.hexify)
        # flags for minimum cta2045 support
        self.support_flags = {
            'intermediate':False,
            'data-link':False,
            'max payload':0
        }
        pass
    def __update_log(self,msg):
        self.log.append(msg)
        self.log = self.log[-self.log_sz:]
        return
    def __write(self,msg,log=False,clear=False):
        sz = 0
        #with self.lock:
            #sz=self.terminal.write("".join(self.log))
            #sz+=self.terminal.write(msg)
        if clear == True:
            print("\n".join(self.log))
            print('-'*20)
        else:
            print(msg)
        if log:
                self.__update_log(msg)
        return
    def __get_input(self):
        valid=False
        try_again=f"{'-'*5}> INVALID. Try again!\n"
        while not valid:
            try:
                msg = "select a command:\n"
                for k,v in choices.items():
                    msg += f"\t {k}: {v}\n"
                self.__write(msg)
                choice=input("nenter a choice: ")
                choice = choices[int(choice)]
                valid=True
            except (KeyError,ValueError):
                self.__write(try_again)
                pass
            except Exception as e:
                tb.print_tb(e)
        return choice
    def __clear(self):
        os.system('clear')
        self.__write('',clear=True)
        return

    def __recv(self):
        res = None
        try:
            res = self.com.recv()
            res = self.cta_mod.from_cta(res)
            if type(res) == dict:
                self.__write(f"<-== receved: {res['command']}",log=True)
                for k,v in res['args'].items():
                    self.__write(f"\t{k} = {v}")
        except TimeoutException as e:
            self.__write(f"<-== waiting for response timeout!",log=True)
            raise TimeoutException # propagate exception
        except Exception as e:
            self.__write(e)
            self.__write("in __recv")
        return res
    def __send(self,cmd,**args):
        ret = False
        c = self.cta_mod.to_cta(cmd,args=args)
        self.com.send(c)
        try:
            self.__write(f'==-> sent {cmd}',log=True)
            if len(args) > 0:
                self.__write('\twith args: ',args)
            ret = True
        except Exception as e:
            self.__write(e)
        return ret

    def __setup(self):
        res = None
        cmds = [('intermediate mtsq','intermediate'),
                ('data-link mtsq','data-link'),
                ('max payload request','max payload')
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
                    if res != None and 'args' in res:
                        self.__send('ack')
                        length = res['args']['max_payload_length']
                        self.support_flags[flag] = int(length)
            except TimeoutException:
                flag = False
                pass
            except Exception as e:
                self.__write(e)
                self.__write('in __setup')
        print(self.support_flags)
        return

    def __run_dcm(self):
        self.__setup()
        while 1:
            c = self.__get_input()
            self.__clear()
            if c == 'quit':
                exit()
            self.__send(c) # sent command
            try:
                response = self.__recv() # wait for link response
                cmd = response['command']
                if not 'nak' in cmd:
                    response = self.__recv() # wait for app response
                    response = response['command']
                    if not 'nak' in response:
                        self.__send('ack')
            except TimeoutException as e:
                # nothing was received from the
                pass
            except Exception as e:
                self.__write(e)
                self.__write("in __run_dcm")
        return
    def __run_der(self):
        last_command = '0x00'
        self.__setup()
        while 1:
            try:
                res = self.__recv() # always waiting for commands
                if res != None:
                    last_command = res['op1']
                    res = res['command']
                    # invoke model with request command -- if supported
                    if cmd in self.FDT:
                        self.FDT[cmd]()
                complement = self.cta.complement(res)
                for cmd in complement:
                    if cmd == 'app ack':
                        self.__send(cmd, last_opcode=last_command)
                    elif cmd == 'nak':
                        self.__send(cmd,nak_reason='unsupported')
                    else:
                        self.__send(cmd)
            except TimeoutException as e:
                # nothing was received from UCM
                continue
            except Exception as e:
                print(e)
        pass
    def run(self):
        if self.mode == 'DER':
            # validate model in DER mode
            assert(abc.issubclass(AbstractModel,self.model))
            self.FDT = {
                'shed':self.model.shed,
                'endshed':self.model.endshed,
                'loadup':self.model.loadup,
                'operating_status':self.model.operating_status,
                'commodity_read':self.model.commodity_read,
            }
            self.__run_der()
        elif self.mode=='DCM':
            self.__run_dcm()
        else:
            raise UnknownModeException(f'Unknown Mode: {self.mode}')
        return



c = CTA2045Device()
c.run()
