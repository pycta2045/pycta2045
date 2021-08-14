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



class DCM:
    prompt = {
        0:"quit",
        1:"shed",
        2:"endshed",
        3:"loadup",
        4: "critical peak event",
        5:"grid emergency",
        6:"operating status request",
    }
    """Renders the time in the center of the screen."""
    def __init__(self):
        self.log = multiprocessing.Queue()
        self.counter = 0
        self.console = Console()
        self.layout = Layout()
        self.layout.split(
            Layout(ratio=1, name="main"),
            Layout(size=10, name="Input"),
        )
        self.layout["main"].split_row(Layout(name="Log"), Layout(name="body", ratio=2))
        self.counter = 0
        pass
    def write(self,msg,log=False,end='\n'):
        if log:
            self.log.put(msg)
            print(",",msg,log,"\nss\n")
        print(msg)
    def render(self) -> Layout:
        self.counter+= 1
        self.layout['body'].update(Text(f"this is a text{self.counter}",style="green"))
        self.layout['Input'].update(Text(self.console.input("henre"),style="red"))
        return self.layout



def main():
    dcm = DCM()

    with Live(dcm.render(), screen=True, redirect_stderr=False) as live:
        try:
            while True:
                live.update(dcm.render())
        except KeyboardInterrupt:
            pass
    # output log
    return
if __name__=="__main__":
    main()