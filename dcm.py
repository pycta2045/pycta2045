#! /bin/python3
from pycta2045 import cta2045device as device
import pandas as pd
from rich.console import Console
from rich import pretty,print
pretty.install()
con = Console()
prompt = {
    0: 'quit',
    1: 'shed',
    2: 'endshed',
    3: 'loadup',
    4: 'critical peak event',
    5: 'grid emergency',
    6: 'operating status request',
    7: 'commodity read request',
    8: 'outside comm connection status',
}
port = '/dev/ttyUSB0'
log_sz = 30
# default mode of operation is DCM
dev = device.SimpleCTA2045Device(comport=port)
dev.run()
complete_log = pd.DataFrame({})
while True:
    con.clear()
    log = dev.get_log()
    complete_log = complete_log.append(log)
    print(complete_log[-log_sz:])
    print(prompt)
    i = input('enter a command to send: ')
    if not i.isdigit() or int(i) not in prompt:
        print(i,'[red]invalid input![/red]')
    else:
        cmd = prompt[int(i)]
        if cmd == 'quit':
            break
        dev.send(cmd)
complete_log.to_csv('logs/DCM_log.csv')
