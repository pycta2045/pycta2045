#! /bin/python3
from pycta2045 import cta2045device as device
import pycta2045.models as models

ev = models.EV()
dev = device.CTA2045Device(mode=device.DER,model=ev,comport='/dev/ttyS7')
log = dev.run()
log.to_csv('logs/DER_log.csv')