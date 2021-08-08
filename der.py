#! /bin/python3
from agents import cta2045device as device
from agents.models import EV

ev = EV()
dev = device.CTA2045Device(mode=device.DER,model=ev,comport='/dev/ttyS7')
dev.run()

