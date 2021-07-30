from agents.com.handler import COM
from agents.cta2045.handler import CTA2045
import sys
import traceback as tb
import threading
import os

class Output:
    def __init__(self,log_size=10):
        '''
            log_size: number of messages to be logged from DER
        '''
        self.log = []
        self.log_sz = log_size
        self.terminal=sys.stdout
        self.lock=threading.Lock()

    def write(self,msg,log=False):
        msg=f"{msg}\n"
        with self.lock:
            self.terminal.write("".join(self.log))
            self.terminal.write(msg)
            if log:
                self.update_log(msg)
        return

    def update_log(self,msg):
        self.log.append(msg)
        self.log=self.log[:-self.log_sz]
        return



out=Output()
choices = {
    1:"shed",
    2:"endshed",
    3:"loadup",
    4:"operating status request",
    5:"quit"
}


cta=CTA2045()
com = COM(checksum=cta.checksum, transform=cta.hexify)

def get_input():
    valid=False
    try_again='====> invalid choice! Try again\n'
    while not valid:
        try:
            for k,v in choices.items():
                out.write(f"\t {k}: {v}")
            choice=input("nenter a choice: ")
            choice = choices[int(choice)]
            valid=True
        except (KeyError,ValueError):
            out.write(try_again)
            pass
        except Exception as e:
            tb.print_tb(e)
    return choice

while 1:
    c = get_input()
    os.system('clear')
    if c=='quit':
        exit()
    out.write('start threading...')
    out.write(f"you entered: {c}")
