from agents import cta2045device as device
from agents.models import EV

ev = EV()
dev = device.CTA2045Device(mode=device.DER,model=ev)
dev.run()
