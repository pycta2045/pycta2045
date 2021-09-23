'''
Author: Mohammed Alsaid (@mohamm-alsaid)
UCM: Universal Control Module
This demonstrates how use the simple UCM provided by pycta2045 library.
'''
import pandas as pd, argparse as ap, select, sys,os
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
