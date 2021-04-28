import matplotlib.pyplot as plt
import numpy as np
import scipy.integrate as sp_int
import argparse


def plot(xs,ys,x_name='Time',vlines = None):
    num = len(ys)//2
    (fig,axs) = plt.subplots(num,num)
    i = 0
    j = 0
    for y,name in ys:
        if i >= num:
            i = 0
            j+=1
        axs[i,j].plot(xs,y)
        if not vlines == None:
            for v in vlines:
                axs[i,j].axvline(v,linestyle='dotted',color='r')
        axs[i,j].set_title(f'{name} vs {x_name}')
        axs[i,j].set(xlabel=x_name,ylabel=name)
        i+=1


class charger:
    def __init__(self,max_volt,max_curr,max_cap,min_comfort,max_comfort):
        self.SOC = []
        self.time = []
        self.power = []
        self.volts = []
        self.currs = []
        self.timer = 0
        self.max_curr = max_curr
        self.max_volt = max_volt
        self.max_cap = max_cap
        self.min_comfort = min_comfort
        self.max_comfort = max_comfort
        return
   
    def charge(current,voltage,time): # returns (power, cap)
    p = current * voltage
    q = current * time
    soc = q/self.max_cap
    return (p,soc)
def update_state(self,c,v,soc,p,t):
    self.time.append(t)
    self.power.append(p)
    self.SOC.append(soc)
    self.volts.append(v)
    self.currs.append(c)
    return
def delay(self,delay):
    times = list(range(delay))
    v = i = 0 # init to 0s
    for t in times:
        p,soc = charge(i,v,t)
        self.update_state(i,v,soc,p,t)
    self.timer = times[-1]
    return

def phase1(SOCs,max_v,max_i):
    v = i = 0 # init to 0s
    while v < max_v:
        v+=1 # increment voltage
        i+=1 # increment current
        self.timer+=1
        v = min(v,max_v)
        i = min(i,min_i)
        p,soc = charge(i,v,t) # calculate power, cap
        self.update_state(i,v,soc,p,t)
    


def phase2():

def phase3():




def update(c,v,soc,p,t):
    ts.append(t)
    ps.append(p)
    SOCs.append(soc)
    volts.append(v)
    currs.append(c)
    return


# https://batteryuniversity.com/learn/article/electric_vehicle_ev
# max_cap => kwh
SOCs = []
ps  =[]
volts = []
currs = []
ts = []
# SOC = soc
time_slots = []
def model(rampup_time=5,rampup_delay = 3,cutoff_soc=0.75,max_cap = 40,max_volt = 230,curr = 15,rate = 0.12,fname='plot',soc=0,max_capacity = 1.):
    max_cap *= 1000 # kwh
    time = 1000
    time = [x for x in range(0,int(time))]
    ramp_volts = max_volt/rampup_time
    print(f'ramp_volts: {ramp_volts}')
    SOC = soc
    i = curr
    v = 0
    min_curr = 2

    

    # =============== first phase ==============
    # charge
    print('\delay PHASE')
    # ramp up delay
    j = 0
    while j < rampup_delay:# and SOC < 0.3:
        t = time.pop(0) # pop a time step
        (power,cap) = charge(i,v,t)
        SOC += (cap/max_cap)
        update(i,v,SOC,power,t)
        print(f'V: {v} I: {i} SOC:{int(SOC*100)}%')
        j += 1
        t = time.pop(0)

    print('\nramp up PHASE')
    # first phase CC (ramp up -- increase volts)
    j = 0
    while j < rampup_time:# and SOC < 0.45:
        (power,cap) = charge(i,v,t)
        SOC += (cap/max_cap)
        update(i,v,SOC,power,t)
        print(f'V: {v} I: {i} SOC:{int(SOC*100)}%')
        v += ramp_volts
        v = min(v,max_volt)
        j += 1
        t = time.pop(0)
        
    print('-'*20,'\n2nd PHASE')
    time_slots.append(t)
    v = max_volt

    # second phase CV/CC (normal charge)
    while SOC < cutoff_soc: 
        (power,cap) = charge(i,v,t)
        SOC += (cap/max_cap)
        update(i,v,SOC,power,t)
        print(f'V: {v} I: {i} SOC:{int(SOC*100)}%')
        t = time.pop(0)
        
    time_slots.append(t-1)
    print('-'*20,'\n3nd PHASE')
    # third phase CV (ramp down -- decrease current)
    while SOC < max_capacity:
        # if i > min_curr:
        i =  i * np.exp(-rate) #np.exp(-t/rate)
        i = max(i,min_curr)  
        (power,cap) = charge(i,v,t)
        SOC = SOC + (cap/max_cap)
        SOC = min(SOC,1)
        update(i,v,SOC,power,t)
        print(f'V: {v} I: {i} SOC:{int(SOC*100)}%')
        t = time.pop(0)
    ys = [(SOCs,'SOC (%)'),(ps,'power (W)'),(currs,'current (A)'),(volts,'voltage (V)')]
    plot(ts,ys,vlines = time_slots)
    plt.tight_layout()
    plt.savefig(f'figs/{fname}.png')


parser = argparse.ArgumentParser(description='Process program args.')
parser.add_argument('-rd', type=int, help='ramp-up delay (sec)',default=3) # in secs

parser.add_argument('-rt', type=int, help='ramp-up time (sec)',default=5) # in secs
parser.add_argument('-o', type=str, help='output file name',default='plot') # png
parser.add_argument('-soc', type=float, help='current SOC (%)',default=0.) # in %

parser.add_argument('-cutoff_soc', type=float, help='transition SOC (%)',default=0.75) # in %

parser.add_argument('-cap', type=int, help='max capacity (kWh)',default=40) # in kwh
parser.add_argument('-v', type=int, help='voltage (V)',default=240) 
parser.add_argument('-c', type=int, help='current (Amp)',default=15) 
parser.add_argument('-dr', type=float, help='decay rate (%)',default=.12)
parser.add_argument('-mc', type=float, help='max capacity (%)',default=1.)




args = parser.parse_args()
rd = args.rd
rt = args.rt
out = args.o
soc = args.soc
cs = args.cutoff_soc
cap = args.cap
v = args.v
c = args.c
dr = args.dr
mc = args.mc

model(rt,rd,cs,cap,v,c,dr,out,soc,mc)
# print(args.accumulate(args.integers))

