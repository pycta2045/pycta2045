"""
Demonstrates a dynamic Layout
"""
from pycta2045 import cta2045 
from pycta2045 import com
import sys, os, pandas as pd, time,  select, traceback as tb, multiprocessing#, import threading
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
        self.log = multiprocessing.Queue()
        self.counter = 0
        self.console = Console()
        self.layout = Layout()
        self.layout.split(
            Layout(ratio=1, name="main"),
            Layout(size=10, name="Input"),
        )
        self.layout["main"].split_row(Layout(name="Log"), Layout(name="body", ratio=2))
        self.cta_mod = cta2045.CTA2045()
        self.com = com.COM(checksum=self.cta_mod.checksum,transform=self.cta_mod.hexify,is_valid=self.cta_mod.is_valid,port=port)
        self.plain_prompt  = list(map(lambda x: f"[{num_color}]{x[0]}[/{num_color}]: [{text_color}]{x[1]}[/{text_color}]",self.prompt.items()))
        self.plain_prompt = "\n".join(self.plain_prompt)
        self.pretty_prompt = Text("").from_markup(self.plain_prompt)
        pass
    def write(self,msg,log=False,end='\n'):
        if log:
            self.log.put(msg)
            print(",",msg,log,"\nss\n")
        print(msg)
        return
    def render(self) -> Layout:
        self.counter+= 1
        self.layout['body'].update(Text(f"\n\nthis is a text{self.counter}",style="green"))
        self.layout['Input'].update(self.pretty_prompt)
        return self.layout
    def update_input_text(self,pretty_text):
        prompt = f"{self.plain_prompt}\n{pretty_text}"
        self.pretty_prompt = self.pretty_prompt.from_markup(prompt)
        self.render()
        return
    def send_command(self,cmd):
        # convert to cta
        cmd_bytes = self.cta_mod.to_cta(cmd)
        self.com.send(cmd_bytes)
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
    with Live(dcm.render(), screen=True, redirect_stderr=False,refresh_per_second=20) as live:
        try:
            while True:
                usr_input = select.select([sys.stdin],[],[],0)
                if usr_input[0]:
                    usr_input = sys.stdin.read(1)
                    sys.stdin.flush()
                    valid_input = validate_input(usr_input,dcm)
                    if valid_input > 0:
                        cmd = dcm.prompt[valid_input]
                        dcm.send_command(cmd)
                        text  = f"[b]sending [{input_color}]{cmd}[/{input_color}]..."
                    elif valid_input == 0:
                        break
                    else:
                        text = f"[b][{warning_color}]INVALID INPUT[/{warning_color}]"
                    dcm.update_input_text(text)
        except KeyboardInterrupt:
            pass
    # output log
    return
if __name__=="__main__":
    main()