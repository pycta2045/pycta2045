import numpy as np, pandas as pd, matplotlib.pyplot as plt
import time, traceback as tb
from .model import CTA2045Model
from pycta2045.cta2045 import CTA2045

power_rating=12.0
operating_status = {
    'endshed':'idle normal',
    'shed':'idle curtailed',
    'loadup':'idle normal',
}

class EV(CTA2045Model):
    def __init__(self,max_volt=240,max_curr=30,max_cap=40,min_comfort=.9,max_comfort=1.,decay_rate=.3,rampup_delay=1,rampup_time=5,verbose=False):
        '''
        Purpose:
            initializes the model with the given parameters for charging
        Args:
            * max_volt: maximum voltage value (volts)
            * max_curr: maximum current value (Amps)
            * min_comfort: minimum user comfort level for SoC (%)
            * max_comfort: maximum user comfort level for SoC (%)
            * decay_rate: rate by which the current decays in constant voltage (CV) phase
            * rampup_delay: rate by which the current decays in constant voltage (CV) phase (time units)
            * rampup_time: time it takes to reach CV phase (time units)
            * max_cap : Nameplate Rating -- Nissan Leaf (Kwh)
            * verbose: print log messages
        Return:
            * None
        NOTES:
            * decay rate: affects the upper half of the graph's concavity (Time v. SoC)
                * larger values >=1 result in a sharper edges when charging reaches max SoC
                * smaller values <1 result in smother edges
                * recommend: default value (0.9)
            * rampup_time: affects the lower half of the graph's concavity (Time v. SoC)
                * larger values >=1 result in more concavity
                * smaller values <1 result in less concavity
                * recommend: default value (1)
        '''
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
        self.max_time = max_cap/power_rating # kWh/kW = hrs
        self.max_time *= 60 * 60  # convert to secs
        self.t_start = time.time()
        self.t_end = int(self.t_start+self.max_time) # calculate when charging should end
        self.decay_rate = decay_rate
        self.rampup_delay = rampup_delay
        self.state = operating_status['endshed']
        # self.t_inc = self.max_curr/self.max_time
        self.t_inc = 1
        self.cta = CTA2045()
        if verbose:
            print(f'min_com: {self.min_comfort}  max: {self.max_comfort} shed: {self.min_shed,self.max_shed}')
        self.init_SoC = 0.0
        return

    def calculate_SoC(self,current,voltage): # returns (power, SoC)
        p = current * voltage
        q = current * self.timer
        # print(self.timer)
        soc = q/self.max_cap
        # print(f'i: {current} p: {p} q: {q} soc: {soc}')
        return (p,soc)
    def current_decay(self,rate,i):
        return i * np.exp(-rate)
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
        self.init_SoC = init_SoC
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
        min_cur = 0.05 * i
        if self.verbose:
            print(f'PHASE3 SoC: {SoC} max: {self.max_comfort} SoC < max : {SoC < self.max_comfort}')
        while SoC < self.max_comfort:
            i = self.current_decay(self.decay_rate,self.currs[-1])
            i = min(self.max_curr,max(i,min_cur))
            p,soc = self.calculate_SoC(i,v) # calculate power, soc
            SoC += soc
            self.timer+=self.t_inc
            self.update_state(i,v,SoC,p)
        return
    def charge(self,init_SoC=.0,fname=None):
        v = self.verbose
        time_slots = []
        self.delay(init_SoC) #<=== to add ramp up delay

        if v:
            print('Charging...')
            print(f'PHASE 1: init SoC: {round(init_SoC,3)}\n')
        time_slots.append(self.time[-1])
        self.phase1(init_SoC)

        if v:
            print(f'PHASE 2: SoC: {round(self.SOC[-1],3)}\n')
        time_slots.append(self.time[-1])
        self.phase2()

        if v:
            print(f'PHASE 3: SoC: {round(self.SOC[-1],3)}\n')
        time_slots.append(self.time[-1])
        self.phase3()




        # calculate the ratio of time / copies
        self.t_ratio = self.max_time//len(self.power)


        time_slots.append(self.time[-1])
        self.time = self.generate_time_stamps()
        # self.time
        ys = [(self.SOC,'SOC (%)'),(self.power,'power (W)'),(self.currs,'current (A)'),(self.volts,'voltage (V)')] # super gross
        if fname != None:
            # self.subplot(self.time,ys,vlines=time_slots,fname=f'{fname}')
            self.plot(self.time,ys[0])
            self.plot(self.time,ys[1])

        d = {'time':self.time,'power':self.power,'soc':self.SOC,'current':self.currs,'voltage':self.volts}

        # print(f'time: {len(self.time)} power: {len(self.power)} SOC: {len(self.SOC)} currs: {len(self.currs)} volts: {len(self.volts)}')
        df = pd.DataFrame(d)
        df.set_index('time',inplace=True)
        self.df = df
        return df
    def generate_time_stamps(self):
        i = self.t_start
        ts = []
        for i in range(int(self.t_start),int(self.t_end)+1,int(self.t_ratio)):
            ts.append(pd.Timestamp(time.ctime(i),unit='s'))
        return ts[:-1]
    def get_soc(self,time):
        '''
            Purpose: returns the SoC at the given Epoch timestamp
            Args:
                * time: unix Epoch timestamp
            Returns: associated SoC
            Notes: Returns None if charging has not started (not plugged-in)
        '''
        try:
            record = self.get_record(time)
            soc = record['soc']
        except Exception as e:
            print(e)
            soc = None
        return soc
    def get_record(self,time):
        '''
            Purpose: returns the record at the given Epoch timestamp
            Args:
                * time: unix Epoch timestamp
            Returns: associated record (time, power, soc, current, voltage)
            Notes: Returns None if charging has not started (not plugged-in)
        '''
        record = None
        try:
            if time >=self.t_end:
                record = self.df.tail(1) # could be 100% or max_comfort (if in shed mode)
            elif time <= self.t_start:
                record = self.df.head(1)
            else:
                # subtract time from the starting time of the charge
                time -= self.t_start
                i = int(time/self.t_ratio)
                record = self.df.iloc[i]
        except Exception as e:
            pass # returns None as record
        return record
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
    def discharge(self,time,rate):
        '''
            Discharges/decreases the battery/SoC based on the given rate for the given time
        '''
        if self.verbose:
            print('Dischargining...')
        if len(self.SOC) == 0:
            if self.verbose:
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
    # ============================ CTA2045 functions =========================
    def shed(self,payload:dict):
        '''
            Purpose: modifies the setpoint
            Args:
                * payload: dict of arguments passed to the function
            Return:
                * val: dict containing return values used for CTA2045
        '''
        print('shedding...')
        val = {}
        self.min_comfort = self.min_shed
        self.max_comfort = self.max_shed
        self.state = operating_status['shed']
        return val
    def endshed(self,payload:dict):
        '''
            Purpose: resets the setpoint
            Args:
                * payload: dict of arguments passed to the function
            Return:
                * val: dict containing return values used for CTA2045
        '''
        print('endshed...')
        val = {}
        self.min_comfort,self.max_comfort = self.user_comfort
        self.state = operating_status['endshed']
        #print(f'new min: {self.min_comfort} new max: {self.max_comfort}')
        return val
    def loadup(self,payload:dict):
        '''
            Purpose: calls the charge function
            Args:
                * payload: dict of arguments passed to the function
            Return:
                * val: dict containing return values used for CTA2045
        '''
        print('loading up...')
        val = {}
        self.state = operating_status['loadup']
        self.charge()
        return val
    def operating_status(self,payload:dict):
        '''
            Purpose: obtain the CTA2045 operating status from the model
            Args:
                * payload: dict of arguments passed to the function
            Return:
                * val: dict containing return values used for CTA2045
        '''
        print('OpStatus...')
        val = {}
        val['op_state_code'] = self.state
        return val
    def commodity_read(self,payload:dict):
        '''
            Purpose: obtain the state (power/SoC) from the model & convert it to commodity values before returning commodity value
            Args:
                * payload: dict of arguments passed to the function
            Return:
                * val: dict containing return values used for CTA2045
            NOTE:
                * a workaround to support multiple Commodity Codes (CC) is to tag CCs after IR values in a "chaining" manner
        '''
        print('CommodityRead...')
        val = {}
        IR = CA = CA2 = IR2 = soc = 0
        val['commodity_code'] = 'electricity consumed' # go with electricity consumed first
        try:
            t = time.time()
            record = self.get_record(t)
            soc = record['soc']
            IR = record['power']
        except TypeError as e: # caused by Nonetype since get_record returns None if charging was not started
            pass # use default IR & CA values
        except Exception as e:
            print(tb.format_tb(e))
            pass
            '''
            # ---------------- calculate electricity consumed -----------------
                >> CA = max_cap(Kwh) * SoC (%)
                >> IR = power[time]
            '''
            CA = self.max_cap * (soc - self.init_SoC)
            IR = CTA2045.hexify(int(IR),length=6)
            CA = CTA2045.hexify(int(CA),length=6)
            '''
            # ---------------- calculate present energy (energy take) ---------
                >> CA = max_cap(Kwh) * (1-SoC) (%)
                >> IR =  None  --> CTA2045 not used
            '''
            CA2 = self.max_cap * (1-soc)


        val['instantaneous_rate'] = CTA2045.hexify(int(IR),length=6)
        CA = CTA2045.hexify(int(CA),length=6)
        CC2 = self.cta.get_code_value('commodity_code','present energy')
        CA2 = CTA2045.hexify(int(CA2),length=6)
        IR2 = CTA2045.hexify(int(IR2),length=6)
        CA = f'{CA} {CC2} {CA2} {IR2}'
        val['cumulative_amount'] = CA



        return val
    def critical_peak_event(self,payload):
        '''
            Purpose: calls the discharge function. If the duration is unknown, the model continously discharge
            Args:
                * payload: dict of arguments passed to the function
            Return:
                * val: dict containing return values used for CTA2045
        '''
        val = {}
        print('critical peak eventing...')
        return val
    def grid_emergency(self,payload):
        '''
            Purpose: calls the discharge function. If the duration is unknown, the model continously discharge
            Args:
                * payload: dict of arguments passed to the function
            Return:
                * val: dict containing return values used for CTA2045
        '''
        val = {}
        print('grid emergencying...')
        return val
