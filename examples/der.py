#! /bin/python3
import time, matplotlib.pyplot as plt, argparse as ap, sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pycta2045 import cta2045device as device
import pycta2045.models as models

def main():
    parser = ap.ArgumentParser()
    parser.add_argument('-p',required=False,type=str,help="com port to use for connection. e.g: -p /dev/ttyS2", default='/dev/ttyS2')
    parser.add_argument('-c',required=True,type=float,help="Capacity of battery (float in kWh)", default=.5)
    args = parser.parse_args()
    port = args.p
    cap = args.c
    figsize = (50,50) # (w,h)
    version = '{cap} kWh' # experiment version
    ev = models.EV(max_cap=cap,verbose=True,decay_rate=.08)
    t_end = ev.t_end
    dev = device.CTA2045Device(mode="DER",model=ev,comport=port)
    log = dev.run(block=True)
    print("LOG: ")
    print(log)
    log.to_csv('logs/DER_log.csv')
    log = ev.get_all_records()

    assert log is not None, "log is None"
    log.to_csv("logs/ev_records_soc.csv")
    log = log[['soc','power']]
    x = log['soc']
    y = log['power']
    print('plotting soc...')
    log.plot(subplots=True)
    plt.savefig(fname=f'figs/ev_records_soc_{version}.png')
    plt.close()

    plt.plot(x,y)
    plt.savefig(f'figs/power_vs_soc_{version}.png')
    plt.close()

    log = ev.get_commodity_log()
    assert log is not None, "log is None"
    log.set_index('time',inplace=True)

    log.to_csv("logs/ev_record_commodity.csv")
    CAs = log[['Elect. Consumed - Cumulative (Wh)','EnergyTake - Cumulative (Wh)']]
    IRs = log[['Elect. Consumed - Inst. Rate (W)']]

    print('plotting time vs CA...')
    CAs.plot() # plot CA
    plt.savefig(fname=f'figs/ev_records_commodity_CA_{version}.png')
    plt.close()

    print('plotting time vs IR...')
    # IRs.plot(figsize=figsize) # plot IR
    IRs.plot() # plot IR
    plt.savefig(fname=f'figs/ev_records_commodity_IR_{version}.png')
    print('closing..')
    plt.close()

if __name__=="__main__":
    main()
    exit()
