#! /bin/python3
from pycta2045 import cta2045device as device



# default mode of operation is DCM
dev = device.CTA2045Device(comport='/dev/ttyS7')
log = dev.run()
log.to_csv('logs/DCM_log.csv')