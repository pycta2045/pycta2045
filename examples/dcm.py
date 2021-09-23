'''
Author: Mohammed Alsaid (@mohamm-alsaid)
UCM: Universal Control Module
This demonstrates how use the simple UCM provided by pycta2045 library.
'''
import pandas as pd, argparse as ap, select, sys,os
# this is used to work around the import system not looking into the parent folder. There are two other ways around this:
# 1. Use a virtual environment & install pycta2045 using: `pip3 install -e .`
#       * This installs pycta2045 lib as an editable package
#       * This might not always work as per PEP 517 see: https://www.python.org/dev/peps/pep-0517/
# 2. Make sure pycta2045 installed to begin with using `pip3 install pycta2045`
# 3. Add the parent dir to the path (i.e. keep the folllowing line of code)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pycta2045 import cta2045device as device
from rich import pretty,print


def main():
    parser = ap.ArgumentParser()
    parser.add_argument('-p',required=False,type=str,help="com port to use for connection. e.g: -p /dev/ttyS2", default='/dev/ttyS2')
    args = parser.parse_args()
    port = args.p
    pretty.install()
    # default mode of operation is DCM
    dev = device.CTA2045Device(comport=port)
    dev.run(block=True)
    log = dev.get_log()
    log.to_csv('logs/DCM_log.csv')
if __name__=="__main__":
    main()
    exit()
