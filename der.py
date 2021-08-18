#! /bin/python3
from pycta2045 import cta2045device as device
import pycta2045.models as models
import time
ev = models.EV(max_cap=.5,decay_rate=2,verbose=True)
t_end = ev.t_end
dev = device.CTA2045Device(mode="DER",model=ev,comport='/dev/ttyS7')
log = dev.run()
print("LOG: ")
print(log)
log.to_csv('logs/DER_log.csv')
log = ev.get_records()
assert log is not None, "log is None"
log.to_csv("logs/ev_records.csv")
