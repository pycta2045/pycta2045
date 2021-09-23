'''
Author: Mohammed Alsaid (@mohamm-alsaid)
This serves as a simple example of how to use the EV model.
'''
import sys,os
# this is used to work around the import system not looking into the parent folder. There are two other ways around this:
# 1. Use a virtual environment & install pycta2045 using: `pip3 install -e .`
#       * This installs pycta2045 lib as an editable package
#       * This might not always work as per PEP 517 see: https://www.python.org/dev/peps/pep-0517/
# 2. Make sure pycta2045 installed to begin with using `pip3 install pycta2045`
# 3. Add the parent dir to the path (i.e. keep the folllowing line of code)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pycta2045.models import ev_model as EV

ev = EV.EV()
ev.charge()
print('start time: ',ev.time[0],"power :",ev.power[0])
print('in between',ev.power[30])
print('end time: ',ev.time[-1],"power: ",ev.power[-1])
print(ev.power)
