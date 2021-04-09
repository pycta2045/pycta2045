import matplotlib.pyplot as pt
import numpy as np
import scipy.integrate as sp_int


def plot(ys,xs,name,y_name,x_name='time'):
    pt.plot(ys,xs)
    pt.xlabel(x_name)
    pt.ylabel(y_name)
    pt.suptitle(f'{y_name} vs {x_name}')
    pt.savefig(name,fmt='png')
    pt.clf()
    return
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

rate = 0.5
ramp_rate = 0.5
max_curr = 15 # amp
min_curr = 0.03 * max_curr
t_max = 1.5 * 60
max_volt = 240
time = list(map(lambda x: 0.5*x,list(range(0,4))))
max_cap = max_curr * t_max
time_step = 1   # minute
t = 0



SOCs = []
ps  =[]
volts = []
currs = []
ts = []
SOC = 0
i = 1
v = 10

# charge
while SOC < 1:
    # first phase CC (ramp up -- increase volts)
    i = max_curr
    while v < max_volt and SOC < 0.45:
        (power,cap) = charge(i,v,t)
        SOC = SOC + (cap/max_cap)
        update(i,v,SOC,power,t)
        print(f'V: {v} I: {i} SOC:{int(SOC*100)}%')
        v += v * ramp_rate
        t += time_step
    print('-'*20)
    v = max_volt
    # second phase CV/CC (normal charge)
    while SOC <= 0.65: 
        (power,cap) = charge(i,v,t)
        SOC = SOC+ (cap/max_cap)
        update(i,v,SOC,power,t)
        print(f'V: {v} I: {i} SOC:{int(SOC*100)}%')
        t += time_step
    print('-'*20)
    # third phase CV (ramp down -- decrease current)
    while i > min_curr and SOC < 1:
        (power,cap) = charge(i,v,t)
        SOC = SOC + (cap/max_cap)
        update(i,v,SOC,power,t)
        print(f'V: {v} I: {i} SOC:{int(SOC*100)}%')
        i -= rate * i
        t += time_step
print(t,t_max)





    # SOC = 1 # to exit


'''
while t < t_max or i == min_curr:
    if v < max_volt:
        v = max_volt#e * v
    if SOC >= 0.8:
        i -= rate * i
    p = f(i,v) # calculate power
    q = f(i,t) # calculate cap
    SOC = q/SOC_max
    volts.append(v)
    currs.append(i)
    print(f'{int(SOC * 100)}%')
    SOCs.append(SOC)
    ps.append(p)
    ts.append(t)


    t = t+time_step
    '''
plot(ts,SOCs,'figs/SOC','SOC')

plot(ts,ps,'figs/power','power')

plot(ts,currs,'figs/current','current')

plot(ts,volts,'figs/volt','voltage')