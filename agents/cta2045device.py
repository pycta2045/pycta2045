from cta2045 import CTA2045
from com import COM
import sys, threading, os, traceback as tb


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



class CTA2045Device:
    def __init__(self,mode=DCM,log_size=10):
        self.mode = mode.__name__
        self.log = []
        self.log_sz = log_size if log_size > 0 else -(log_size-1)
        self.terminal = sys.stdout
        self.lock = threading.Lock()
        self.screen_sz = 0
        pass
    def __update_log(self,msg):
        self.log.append(msg)
        self.log = self.log[:-self.log_sz]
        return
    def __write(self,msg,log=False,clear=False):
        msg=f'{msg}\n'
        sz = 0
        with self.lock:
            sz=self.terminal.write("".join(self.log))
            sz+=self.terminal.write(msg)
            if log:
                self.__update_log(msg)
            if not clear:
                self.screen_sz += sz
        return
    def __get_input(self):
        valid=False
        try_again=f"{'-'*5}> INVALID. Try again!\n"
        while not valid:
            try:
                for k,v in choices.items():
                    self.__write(f"\t {k}: {v}")
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
        self.__write('\r' *self.screen_sz,clear=True)
        self.screen_sz = 0
        return

    def run(self):
        while 1:
            c = self.__get_input()
            self.__clear()
            if c == 'quit':
                exit()
        return






c = CTA2045Device(DER,log_size=-2)
print('working!')
c.run()
