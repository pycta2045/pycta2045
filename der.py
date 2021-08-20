#! /bin/python3
from pycta2045 import cta2045device as device
import pycta2045.models as models
import time
import matplotlib.pyplot as plt
from rich import pretty
pretty.install()


figsize = (50,50) # (w,h)
version = '_1_5_k_max_cap' # experiment version

ev = models.EV(max_cap=1.5,verbose=True)
t_end = ev.t_end
dev = device.CTA2045Device(mode="DER",model=ev,comport='/dev/ttyUSB0')
log = dev.run()
print("LOG: ")
print(log)
log.to_csv('logs/DER_log.csv')
log = ev.get_records()

assert log is not None, "log is None"
log.to_csv("logs/ev_records_soc.csv")
log = log[['soc','power','current','voltage']]
print('plotting soc...')
# log.plot(subplots=True,figsize=figsize)
log.plot(subplots=True)
plt.savefig(fname=f'figs/ev_records_soc{version}.png')
plt.close()

log = ev.get_commodity_log()
assert log is not None, "log is None"
log.set_index('time',inplace=True)

log.to_csv("logs/ev_record_commodity.csv")
CAs = log[['Elect. Consumed - Cumulative (Wh)','EnergyTake - Cumulative (Wh)']]
IRs = log[['Elect. Consumed - Inst. Rate (W)','EnergyTake - Inst. Rate (W)']]

print('plotting time vs CA...')
# CAs.plot(figsize=figsize) # plot CA
CAs.plot() # plot CA
plt.savefig(fname=f'figs/ev_records_commodity_CA{version}.png')
plt.close()

print('plotting time vs IR...')
# IRs.plot(figsize=figsize) # plot IR
IRs.plot() # plot IR
plt.savefig(fname=f'figs/ev_records_commodity_IR{version}.png')
plt.close()
