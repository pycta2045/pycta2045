"""
Demonstrates a dynamic Layout
"""
from pycta2045 import SimpleCTA2045Device
import sys, os, pandas as pd, time,  select, traceback as tb, threading 
from queue import Queue
from datetime import datetime
from time import sleep

from rich.align import Align
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.text import Text

num_color = 'red'
text_color = 'cyan'
input_color = 'magenta'
warning_color = 'bright_red'
log_color_style = 'pale_violet_red1'
class DCM: 
    prompt = {
        0: 'quit',
        1: 'shed',
        2: 'endshed',
        3: 'loadup',
        4: 'critical peak event',
        5: 'grid emergency',
        6: 'operating status request',
    }
    def __init__(self,port='/dev/ttyS6'):
        self.counter = 0
        self.console = Console()
        self.layout = Layout()
        self.layout.split(
            Layout(name="header", size=1),
            Layout(ratio=1, name="Output"),
            Layout(size=10, name="Input"),
        )
        self.plain_prompt  = list(map(lambda x: f"[{num_color}]{x[0]}[/{num_color}]: [{text_color}]{x[1]}[/{text_color}]",self.prompt.items()))
        self.plain_prompt = "\t".join(self.plain_prompt)
        self.pretty_prompt = Text("").from_markup(self.plain_prompt,justify='center')
        self.device = SimpleCTA2045Device()
        self.device.run()
        self.log = self.device.get_log()
        self.log_size = 20
        return
    def write(self,msg,log=False,end='\n'):
        if log:
            self.log.put(msg)
            print(",",msg,log,"\nss\n")
        print(msg)
        return
    def render(self) -> Layout:
        # grab log from device 
        log = self.device.get_log()
        # display log
        self.log = self.log.append(log)
        self.layout['Output'].update(Text(f"{self.log.tail(self.log_size)}",style=log_color_style,justify='center'))
        self.layout['header'].update(Text(datetime.now().ctime(), style="bold magenta", justify="center"))
        self.layout['Input'].update(self.pretty_prompt)
        return self.layout
    def update_input_text(self,pretty_text):
        prompt = f"{self.plain_prompt}\n{pretty_text}"
        self.pretty_prompt = self.pretty_prompt.from_markup(prompt,justify='center')
        self.render()
        return
    def send_command(self,cmd):
        self.device.send(cmd)
        return
def validate_input(text,dcm) -> str:
    if text.isdigit():
        num = int(text)
        if num in dcm.prompt:
            return num 
    return -1 

def main():
    dcm = DCM()
    con = Console()
    terminated = False
    q = Queue()
    def usr_input():
        try:
            while not terminated:
                inp,_,_ = select.select([sys.stdin],[],[],0)
                if inp:
                    for l in sys.stdin:
                        q.put(l.strip())
                    sys.stdin.flush()
                
        except Exception:
            return
    
    with Live(dcm.render(), screen=True, redirect_stderr=False,refresh_per_second=20) as live:
        try:
            thread = threading.Thread(target=usr_input)
            thread.daemon = True
            thread.start()
            text = f"[b]Enter a choice"
            while True:
                if not q.empty():
                    inp = q.get()
                    valid_input = validate_input(inp,dcm)
                    if valid_input > 0:
                        cmd = dcm.prompt[valid_input]
                        dcm.send_command(cmd)
                        text  = f"[b]Sending [{input_color}]{cmd}[/{input_color}]..."
                    elif valid_input == 0:
                        break
                    else:
                        text = f"[b][{warning_color}]INVALID INPUT {inp}[/{warning_color}]"
                dcm.update_input_text(text)
        except KeyboardInterrupt:
            pass
    dcm.device.stop()
    terminated = True
    thread.join()
    # count
    # thread_count = threading.active_count()

    for t in threading.enumerate():
        print(t)
    # output log
    save = ''
    while not save in ['y','n']:
        if not save in ['','y','n']:
            print('invalid input! ',save) 
        print(f"count: {thread_count} would you like to save the log? [y/n]")
        save = input(f"")
        save = save.lower()
    fname = ''
    if save == 'y' and fname == '':
        fname = input('Enter output log name (csv): ')
        dcm.log.to_csv(f"{fname}.csv")
    return
if __name__=="__main__":
    main()