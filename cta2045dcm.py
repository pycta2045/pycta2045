#! /bin/python3
from agents import cta2045device as device

dev = device.CTA2045Device(mode=device.DCM,comport='/dev/ttyUSB0')
dev.run()
