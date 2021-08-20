#! /bin/python3
from pycta2045 import cta2045device as device


port = '/dev/ttyS100'
# default mode of operation is DCM
dev = device.CTA2045Device(comport=port)
log = dev.run()
log.to_csv('logs/DCM_log.csv')