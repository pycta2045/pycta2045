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


def decay(x,m,t,b):
    i = m * np.exp(-t*x)+b
    # print(f'x: {x}, m :{m}, t: {t}, b: {b} exp: {np.exp(-t*x)}= {i}')
    return i

class charger:
    def __init__(self,max_volt,max_curr,max_cap,min_comfort,max_comfort,decay_rate,rampup_delay,rampup_time=5,verbose=False):
        self.SOC = []
        self.time = []
        self.power = []
        self.volts = []
        self.currs = []
        self.timer = 0
        self.max_curr = max_curr
        self.max_volt = max_volt
        self.max_cap = max_cap * 1000 # in Kwh
        self.min_comfort = min_comfort
        self.max_comfort = max_comfort
        self.user_comfort = (min_comfort,max_comfort)
        self.min_shed = min_comfort - 0.2 # drop by 20%
        self.max_shed = max_comfort - 0.1 # drop by 10% 
        self.verbose = verbose
        self.rampup_time = rampup_time
        self.decay_rate = decay_rate
        self.rampup_delay = rampup_delay
        self.t_inc = 1
        print(f'min_com: {self.min_comfort}  max: {self.max_comfort} shed: {self.min_shed,self.max_shed}')# soc: {SoC}')

        return
   
    def calculate_SoC(self,current,voltage): # returns (power, SoC)
        p = current * voltage
        q = current * self.timer
        soc = q/self.max_cap
        # print(f'i: {current} p: {p} q: {q} soc: {soc}')
        return (p,soc)

    def update_state(self,c,v,soc,p):
        self.time.append(self.timer)
        self.power.append(p)
        max_soc = self.max_comfort
        self.SOC.append(min(soc,max_soc))
        self.volts.append(v)
        self.currs.append(c)
        if self.verbose:
            print(f'V: {v} I: {c} SOC:{int(soc*100)}%')
        return

    def delay(self,init_SoC):
        times = list(range(self.rampup_delay+1))
        v = i = 0 # init to 0s
        SoC = init_SoC
        for t in times:
            self.timer +=self.t_inc
            p,soc = self.calculate_SoC(i,v)
            SoC += soc
            self.update_state(i,v,SoC,p)
        return

    def phase1(self,init_SoC):
        v = i = 0 # init to 0s
        SoC = init_SoC
        ramp_volts = self.max_volt / self.rampup_time # to calculate how long it should take to reach max volts in given ramp up time
        ramp_curr = self.max_curr/self.rampup_time
        while v < self.max_volt and SoC < self.min_comfort and SoC < self.max_comfort:
            v+=ramp_volts # increment voltage
            i+=ramp_curr # increment current
            v = min(v,self.max_volt)
            i = min(i,self.max_curr)
            p,soc = self.calculate_SoC(i,v) # calculate power, soc
            SoC += soc
            self.timer+=self.t_inc
            self.update_state(i,v,SoC,p)
        return
    def phase2(self):
        v = self.max_volt
        i = self.max_curr
        SoC = self.SOC[-1]      
        while SoC < self.min_comfort and SoC < self.max_comfort:
            self.timer+=self.t_inc
            p,soc = self.calculate_SoC(i,v) # calculate power, soc
            SoC += soc
            self.update_state(i,v,SoC,p)
        return
    def phase3(self):
        v = self.max_volt
        i = self.max_curr
        SoC = self.SOC[-1]
        j = 0
        min_cur = 0.05 * i
        print(f'PHASE3 SoC: {SoC} max: {self.max_comfort} SoC < max : {SoC < self.max_comfort}')
        while SoC < self.max_comfort:
            i = decay(self.decay_rate/1000,i,self.time[-1],self.decay_rate)
            i = min(self.max_curr,max(i,min_cur))
            p,soc = self.calculate_SoC(i,v) # calculate power, soc
            SoC += soc
            self.timer+=self.t_inc
            self.update_state(i,v,SoC,p)
        return
    def charge(self,init_SoC=.0,fname=None):
        print('Charging...\n')
        time_slots = []
        self.delay(init_SoC) #<=== to add ramp up delay

        time_slots.append(self.time[-1])
        self.phase1(init_SoC)

        time_slots.append(self.time[-1])
        self.phase2()


        time_slots.append(self.time[-1])
        self.phase3()


        time_slots.append(self.time[-1])
        ys = [(self.SOC,'SOC (%)'),(self.power,'power (W)'),(self.currs,'current (A)'),(self.volts,'voltage (V)')] # super gross
        if fname != None:
            # self.subplot(self.time,ys,vlines=time_slots,fname=f'{fname}')
            self.plot(self.time,ys[0])
            self.plot(self.time,ys[1])
        return self.SOC

    def subplot(self,xs,ys,x_name='Time',vlines = None,fname=None): # change to use member variables not args
        num = len(ys)//2 # divide graphs by 2
        (fig,axs) = plt.subplots(num,num) # create 4 graphs
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
        plt.tight_layout()
        if not fname==None:
            plt.savefig(f'figs/{fname}.png')
        else:
            plt.show()
        return
    def plot(self,xs,ys,x_name='Time',vlines = None,show=False): # change to use member variables not args
        plt.clf()
        ys,y_name = ys
        plt.plot(xs,ys)
        plt.xlabel(x_name)
        plt.ylabel(y_name)
        # print(x_name,xs)
        # print(y_name,ys)
        plt.savefig(f'figs/{x_name}_v_{y_name}.png')
        if show:
            plt.show()
        return
    def shed(self):
        self.min_comfort = self.min_shed
        self.max_comfort = self.max_shed
        return
    def endshed(self):
        self.min_comfort,self.max_comfort = self.user_comfort
        # print(f'new min: {self.min_comfort} new max: {self.max_comfort}')
        return
    def discharge(self,time,rate):
        '''
            Discharges/decreases the battery/SoC based on the given rate for the given time
        '''
        print('Dischargining...')
        if len(self.SOC) == 0:
            print('Discharging an empty battery!\n')
            return
        soc = self.SOC[-1]
        v = self.volts[-1]
        i = self.currs[-1]
        p = self.power[-1]
        for t in range(time):
            self.timer+=self.t_inc
            soc -= rate*soc
            self.update_state(i,v,soc,p)
        return soc

            
            


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
parser.add_argument('-rd', type=int, help='ramp-up delay (sec)',default=0) # in secs

parser.add_argument('-rt', type=int, help='ramp-up time (sec)',default=1) # in secs (min = 1 as we divide by rt in the first phase)
parser.add_argument('-o', type=str, help='output file name',default='plot') # png
parser.add_argument('-soc', type=float, help='current SOC (%)',default=0.) # in %

parser.add_argument('-cutoff_soc', type=float, help='transition SOC (%)',default=0.75) # in %

parser.add_argument('-cap', type=int, help='max capacity (kWh)',default=40) # in kwh
parser.add_argument('-v', type=int, help='voltage (V)',default=240) 
parser.add_argument('-c', type=int, help='current (Amp)',default=15) 
parser.add_argument('-dr', type=float, help='decay rate (%)',default=1.)
parser.add_argument('-mc', type=float, help='max capacity (%)',default=1.)
parser.add_argument('-verb', type=bool, help='verbose',default=False)

parser.add_argument('-min', type=float, help='minimum user comfort',default=.95)

parser.add_argument('-max', type=float, help='maximum user comfort',default=1.)


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
verb = args.verb
max_com = args.max
min_com = args.min

# model(rt,rd,cs,cap,v,c,dr,out,soc,mc)
c = charger(v,c,cap,min_comfort=min_com,max_comfort=max_com,rampup_time = rt,decay_rate=dr,rampup_delay=rd,verbose=verb) #self,max_volt,max_curr,max_cap,min_comfort,max_comfort


for i in range(2):
    soc = c.charge(soc)[-1]
soc = c.discharge(16,0.03)
c.shed()
for i in range(3):
    for i in range(10):
        soc = c.charge(soc)[-1]
    soc = c.discharge(15,0.03)
# soc = c.charge(soc)[-1]

c.endshed()

for i in range(2):
    soc = c.charge(soc)[-1]
# soc = c.charge(soc)[-1]

# soc = c.charge(soc)[-1]


# c.shed()
# soc = c.charge(soc)[-1]

# soc = c.charge(soc)[-1]

# c.endshed()
# soc = c.charge(soc)[-1]

soc = c.charge(soc,fname=out)[-1]
