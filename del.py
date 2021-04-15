import matplotlib.pyplot as plt
import numpy as np
import scipy.integrate as sp_int


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
    # for a in axs.flat:
        # a.set(xlabel=x_name)
        
    # pt.plot(xs,ys)
    # pt.xlabel(x_name)
    # pt.ylabel(y_name)
    # pt.suptitle(f'{y_name} vs {x_name}')
    # pt.savefig(name,fmt='png')
    # pt.clf()
    return plt
def f(i,v):
    return i*v
def charge(current,voltage,time): # returns (power, cap)
    p = current * voltage
    q = current * time
    return (p,q)
def update(c,v,soc,p,t):
    ts.append(t)
    ps.append(p)
    SOCs.append(soc)
    volts.append(v)
    currs.append(c)
    return


# https://batteryuniversity.com/learn/article/electric_vehicle_ev
rate = 0.1
curr_steps = 4
curr = 15 # amp
min_curr = 2
# t_max = 1.5
max_volt = 230
max_cap = 30 * 1000 # kwh
# time_step = 0.9   # minute
cutoff_soc = 0.75

ramp_up_delay = 3 # time steps
rampup_time = 5 # time stemps

# time = t_max//time_step
time = 100
time = [x for x in range(0,int(time))]


ramp_volts = max_volt/rampup_time
print(f'ramp_volts: {ramp_volts}')

SOCs = []
ps  =[]
volts = []
currs = []
ts = []
SOC = 0
i = curr
v = 5
time_slots = []

# =============== first phase ==============
# charge
print('\delay PHASE')
# ramp up delay
j = 0
while j < ramp_up_delay:# and SOC < 0.3:
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
while SOC < 1:
    # if i > min_curr:
    i -= (rate * i)
    i = max(i,min_curr)  
    (power,cap) = charge(i,v,t)
    SOC = SOC + (cap/max_cap)
    SOC = min(SOC,1)
    update(i,v,SOC,power,t)
    print(f'V: {v} I: {i} SOC:{int(SOC*100)}%')
    t = time.pop(0)
    
# print(t,t_max)



ys = [(SOCs,'SOC (%)'),(ps,'power (W)'),(currs,'current (A)'),(volts,'voltage (V)')]
plot(ts,ys,vlines = time_slots)
plt.tight_layout()
plt.savefig('figs/plot.png')
