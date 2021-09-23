'''
Author: Mohammed Alsaid (@mohamm-alsaid)
This is an example of a simple DCM that uses rich library to display the log in a table format (TUI). It serves as an example of how to use pycta2045 library. 
'''
import datetime as dt, select, sys, os, pandas as pd, json, argparse as ap
# this is used to work around the import system not looking into the parent folder. There are two other ways around this:
# 1. Use a virtual environment & install pycta2045 using: `pip3 install -e .`
#       * This installs pycta2045 lib as an editable package
#       * This might not always work as per PEP 517 see: https://www.python.org/dev/peps/pep-0517/
# 2. Make sure pycta2045 installed to begin with using `pip3 install pycta2045`
# 3. Add the parent dir to the path (i.e. keep the folllowing line of code)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from datetime import datetime
from pycta2045 import CTA2045Device
from time import sleep
from rich.table import Table
from queue import Queue
from threading import Thread
from rich.align import Align
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.live import Live
from rich.text import Text

EMPTY_SLOT = 40
LOG_SIZE = 10

log = ['-'*EMPTY_SLOT]*LOG_SIZE
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
output = f"Choose from the following menu\n{output}\n[bold]To Exit: CTRL-C + ENTER[/bold]\n\n"

class Clock:
    """Renders the time in the center of the screen."""

    def __rich__(self) -> Text:
        return Text(datetime.now().ctime(), style="bold magenta", justify="center")

def update_table(log):
    table = Table(title="Log",show_lines=True,min_width=3*EMPTY_SLOT)
    table.add_column("Timestamp", style="cyan", no_wrap=True)
    table.add_column("Event", style="magenta")
    table.add_column("arguments", justify="right", style="green")
    if type(log) == pd.DataFrame:
        for index, entry in log.tail(LOG_SIZE).iterrows():
            args = '-' * EMPTY_SLOT if len(entry['arguments']) == 2 else entry['arguments']
            if not '--' in args and len(args) > 3: # parse back into dict & process it
                args = args.replace("'",'"')
                args = args.replace("\\x00",'')
                args = json.loads(args)
                args = '\n'.join(map(lambda x: f'{x[0]}: {x[1]}',args.items()))
            ts = dt.datetime.fromtimestamp(float(index))
            table.add_row(f'{ts}', entry['event'], Text(args,justify='left'))
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
def centered_text(text):
    return Align.center(
        Text(text,justify='left')
    )
def wrapped_text(text):
    return Align.center(Panel.fit(Text.from_markup(text,justify='left')))

# =================== parse args =====================
parser = ap.ArgumentParser()
parser.add_argument('-p',required=False,type=str,help="com port to use for connection. e.g: -p /dev/ttyS2", default='/dev/ttyS2')
args = parser.parse_args()
port = args.p
# =================== end of parsing =====================
# =================== create layout ======================
console = Console()
layout = Layout()

layout.split(
    Layout(name="header", size=1),
    Layout(ratio=1, name="body"),
    Layout(size=len(prompt)+6, name="footer"),
)

layout["body"].update(
    Align.center(
        update_table(["something"]*10),
        vertical="middle",
    )
)

layout['footer'].update(wrapped_text(output))
layout["header"].update(Clock())
# =================== create CTA2045 device ==================
q = Queue()
thread = Thread(target=get_input)
thread.daemon=True
stopped = False
thread.start()
dev = CTA2045Device(comport=port)
dev.run()

# =================== start the TUI loop =====================

with Live(layout, screen=True, redirect_stderr=False) as live:
    try:
        while True:
            sleep(.05)
            layout["body"].update(Align.center(update_table(log),vertical="middle"))
            if not q.empty():
                i = q.get()
                if valid(i):
                    dev.send(prompt[i])
                    new = f"{output}Sending: [cyan]{prompt[i]}[/cyan]..."
                else:
                    new = f"{output}[red]INVALID INPUT![/red]"
                layout["footer"].update(wrapped_text(new))
            log = dev.get_log()
    except KeyboardInterrupt:
        stopped = True
        dev.stop()
        thread.join()
        pass
