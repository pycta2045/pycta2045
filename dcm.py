#! /bin/python3
from pycta2045 import cta2045device as device
import pandas as pd, argparse as ap, select, sys,os
from rich.console import Console
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