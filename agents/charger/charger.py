import numpy as np
import matplotlib.pyplot as plt
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
