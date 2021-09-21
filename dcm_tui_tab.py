from datetime import datetime
from pycta2045 import CTA2045Device
from time import sleep
from rich.table import Table
import datetime as dt, select, sys, pandas as pd
from queue import Queue
from threading import Thread
from rich.align import Align
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.text import Text

EMPTY_SLOT = 40
LOG_SIZE = 10

log = ['-'*EMPTY_SLOT]*LOG_SIZE
full_log = pd.DataFrame({})
prompt = {
        '1':'shed',
        '2':'endshed',
        '3':'loadup',
        '4':'commodity read request',
        '5':'device info request',
        '6':'outside comm connection status',
        '7':'operating status request',
}
output = list(prompt.items())
output = "\n".join(map(lambda x: f"{x[0]} to {x[1]}",output))
output = f"Choose from the following menu\n{output}\nTo Exit: CTRL-C + ENTER\n\n"

def update_table(log):
    table = Table(title="Log")
    table.add_column("Timestamp", style="cyan", no_wrap=True)
    table.add_column("Event", style="magenta")
    table.add_column("arguments", justify="right", style="green")
    if type(log) == pd.DataFrame:
        print(log.columns)
        for index, entry in log.tail(LOG_SIZE).iterrows():
            args = '-' * EMPTY_SLOT if len(entry['arguments']) == 2 else entry['arguments']
            ts = dt.datetime.fromtimestamp(float(index))
            table.add_row(f'{ts}', entry['event'], args)
    return table
def get_input():
    global q
    global stopped
    while not stopped:
        i = input()
        q.put(i.strip())
    return
def valid(inp):
    return inp in prompt

console = Console()
layout = Layout()

layout.split(
    Layout(name="header", size=1),
    Layout(ratio=1, name="body"),
    Layout(size=10, name="footer"),
)

#layout["main"].split_row(Layout(name="side"), Layout(name="body", ratio=2))

#layout["side"].split(Layout(), Layout())

layout["body"].update(
    Align.center(
        update_table(["something"]*10),
        vertical="middle",
    )
)

class Clock:
    """Renders the time in the center of the screen."""

    def __rich__(self) -> Text:
        return Text(datetime.now().ctime(), style="bold magenta", justify="center")


layout['footer'].update(Text(output,justify="center"))
layout["header"].update(Clock())
q = Queue()
thread = Thread(target=get_input)
thread.daemon=True
stopped = False
thread.start()
dev = CTA2045Device(comport='/dev/ttyS100')
dev.run()


with Live(layout, screen=True, redirect_stderr=False) as live:
    try:
        while True:
            sleep(.05)
            layout["body"].update(Align.center(update_table(log),vertical="middle"))
            if not q.empty():
                i = q.get()
                if valid(i):
                    dev.send(prompt[i])
                    new = f"{output}Sending: {prompt[i]}..."
                else:
                    new = f"{output}INVALID INPUT!"
                layout["footer"].update(Text(new,justify="center"))
            full_log = full_log.append(dev.get_log())
            log = full_log
    except KeyboardInterrupt:
        stopped = True
        dev.stop()
        sleep(1)
        exit()
        pass

