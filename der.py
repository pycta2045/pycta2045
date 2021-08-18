#! /bin/python3
from pycta2045 import cta2045device as device
import pycta2045.models as models
import time
import matplotlib.pyplot as plt


figsize = (500,500) # (w,h)
version = '_500_max_cap' # experiment version

ev = models.EV(max_cap=.5,decay_rate=2)
t_end = ev.t_end
dev = device.CTA2045Device(mode="DER",model=ev,comport='/dev/ttyS7')
log = dev.run()
print("LOG: ")
print(log)
log.to_csv('logs/DER_log.csv')
log = ev.get_records()
assert log is not None, "log is None"
log.to_csv("logs/ev_records_soc.csv")

log.plot(subplots=True,figsize=figsize)
plt.savefig(fname='figs/ev_records_soc.png')
plt.close()



log = ev.get_commodity_log()
assert log is not None, "log is None"
log.set_index('time',inplace=True)

log.to_csv("logs/ev_record_commodity.csv")
CAs = log[['Elect. Consumed - Cumulative (Wh)','EnergyTake - Cumulative (Wh)']]
IRs = log[['Elect. Consumed - Inst. Rate (W)','EnergyTake - Inst. Rate (W)']]

CAs.plot(figsize=figsize) # plot CA
plt.savefig(fname='figs/ev_records_commodity_CA.png')
plt.close()
IRs.plot(figsize=figsize) # plot IR
plt.savefig(fname='figs/ev_records_commodity_IR.png')
plt.close()

