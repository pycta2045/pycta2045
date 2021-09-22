import sys, traceback as tb, threading, os, argparse
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pycta2045 import COM
from pycta2045 import CTA2045

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



parser = argparse.ArgumentParser()
parser.add_argument('-p',required=True,type=str,help="com port to use for connection. e.g: -p /dev/ttyS2", default='/dev/ttyS2')
args = parser.parse_args()
port = args.p

cta=CTA2045()
com = COM(checksum=cta.checksum, transform=cta.hexify,is_valid=cta.is_valid,port=port)
while 1:
    c = get_input()
    os.system('clear')
    if c=='quit':
        exit()
    out.write('start threading...')
    out.write(f"sent: {c}")
    com.send(cta.to_cta(c))
