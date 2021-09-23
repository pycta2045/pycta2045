'''
Author: Mohammed Alsaid (@mohamm-alsaid)
This serves as a simple example of how to use the EV model.
'''
import sys,os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pycta2045.models import ev_model as EV

ev = EV.EV()
ev.charge()
print('start time: ',ev.time[0],"power :",ev.power[0])
print('in between',ev.power[30])
print('end time: ',ev.time[-1],"power: ",ev.power[-1])
print(ev.power)
