import numpy as np, pandas as pd, matplotlib.pyplot as plt
import time, traceback as tb
from datetime import datetime as dt
from .model import CTA2045Model
from pycta2045.cta2045 import CTA2045

operating_status = {
    'unplugged':'idle opted out',
    'endshed':'idle normal',
    'shed':'idle curtailed',
    'loadup':'idle normal',
    'grid emergency':'idle normal',
    'critical peak event':'idle normal',
}

class EV(CTA2045Model):
    def __init__(self,initial_soc=0.0,max_volt=240,max_curr=30,max_cap=40,min_comfort=.8,max_comfort=1.,decay_rate=.5,rampup_delay=1,rampup_time=5,t_res=1,verbose=False):
        '''
        Purpose:
            initializes the model with the given parameters for charging
        Args:
            * max_volt: maximum voltage value (volts)
            * max_curr: maximum current value (Amps)
            * min_comfort: minimum user comfort level for SoC (%)
            * max_comfort: maximum user comfort level for SoC (%)
            * decay_rate: rate by which the current decays in constant voltage (CV) phase <------------------- NO LONGER USED & SHOULD BE REMOVED -- ALSO REMOVE ARG DEFAULTS (DEL)
            * rampup_delay: rate by which the current decays in constant voltage (CV) phase (time units)
            * rampup_time: time it takes to reach CV phase (time units)
            * max_cap : Nameplate Rating -- Nissan Leaf (Kwh)
            * t_res: time resolution, which is used as increments/beat everythin is calculated by
            * verbose: print log messages
        Return:
            * None
        NOTES:
            * decay rate: affects the upper half of the graph's concavity (Time v. SoC) <------------------- NO LONGER USED & SHOULD BE REMOVED -- ALSO REMOVE ARG DEFAULTS (DEL)
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
        self.power_rating = max_curr * max_volt
        self.max_cap = max_cap * 1000 # in Kwh
        # ------------- normal setpoints --------------------
        self.min_comfort = min_comfort
        self.max_comfort = max_comfort
        self.user_comfort = (min_comfort,max_comfort)
        # ------------- shed setpoints --------------------
        self.min_shed = min_comfort - (min_comfort*0.2) # drop by 20%
        self.max_shed = max_comfort - (max_comfort*0.1) # drop by 10%
        # ------------- GridEmergency setpoints --------------------
        self.min_ge = min_comfort * 0.0
        self.max_ge = max_comfort * 0.0
        # ------------- Critical Peak Event setpoints --------------------
        self.min_cpe = min_comfort * 0.5
        self.max_cpe = max_comfort * 0.5

        self.verbose = verbose
        self.rampup_time = rampup_time
        self.max_time = self.max_cap/self.power_rating # kWh/kW = hrs
        self.max_time *= 60 * 60  # convert to secs
        self.t_start = np.ceil(time.time())
        self.t_end = np.ceil(self.t_start+self.max_time) # calculate when charging should end
        self.decay_rate = decay_rate
        self.rampup_delay = rampup_delay
        self.state = operating_status['unplugged']
        # self.t_inc = self.max_curr/self.max_time
        self.init_SoC = initial_soc
        self.t_inc = t_res
        self.cta = CTA2045()
        if verbose:
            print(f'min_com: {self.min_comfort}  max: {self.max_comfort} shed: {self.min_shed,self.max_shed}')
        self.init_SoC = 0.0
        self.commodity_log = pd.DataFrame({})
        return

    def calculate_SoC(self,current,voltage): # returns (power, SoC)
        p = current * voltage
        q = current * self.timer
        # print(self.timer)
        soc = q/self.max_cap
        # print(f'i: {current} p: {p} q: {q} soc: {soc}')
        return (p,soc)
    def current_decay(self,curr):
        '''
            This function should only be used in the 3rd phase of charging (Constant Voltage).
            That means we shouldn't have an issue with dividing by zero.
        '''
        # current_cap = self.max_cap*soc
        soc = self.SOC[-1]
        decay = curr* np.exp(soc - self.max_comfort - .06)
        return decay
    def update_state(self,c,v,soc,p):
        decimal = 3
        p = np.round(p,decimals=decimal)
        c = np.round(c,decimals=decimal)
        v = np.round(v,decimals=decimal)
        soc = np.round(soc,decimals=decimal)
        self.time.append(self.timer)
        self.power.append(p)
        max_soc = self.max_comfort
        f_soc = min(soc,max_soc)
        self.SOC.append(f_soc)
        self.volts.append(v)
        self.currs.append(c)
        if self.verbose:
            print(f'V: {v} I: {c} SOC: {int(soc*100)}%')
        return
    def delay(self,init_SoC):
        times = list(range(self.rampup_delay+1))
        v = i = 0 # init to 0s
        # grab last values if exist
        if len(self.volts)>0 and len(self.currs)>0:
            i = self.currs[-1]
            v = self.volts[-1]
        self.init_SoC = init_SoC
        SoC = init_SoC
        for t in times:
            self.timer +=self.t_inc
            p,soc = self.calculate_SoC(i,v)
            SoC += soc
            self.update_state(i,v,SoC,p)
        return
    def phase1(self,init_SoC):
        v = self.max_volt
        i = 0 # init to 0s
        SoC = init_SoC
        #ramp_volts = self.max_volt / self.rampup_time # to calculate how long it should take to reach max volts in given ramp up time
        ramp_curr = self.max_curr/self.rampup_time # to calculate how long it should take to reach max volts in given ramp up time
        while v < self.max_volt and SoC < self.min_comfort and SoC < self.max_comfort:
            #v+=ramp_volts # increment voltage
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
        while SoC < self.min_comfort and SoC < self.max_comfort:#and SoC < self.max_comfort and SoC < .7:
            # print(2**SoC)
            self.timer+=self.t_inc
            p,soc = self.calculate_SoC(i,v) # calculate power, soc
            SoC += soc
            self.update_state(i,v,SoC,p)
        return
    def phase3(self):
        v = self.max_volt
        i = self.max_curr
        SoC = self.SOC[-1]
        min_cur = 0.0005 * i
        if self.verbose:
            print(f'PHASE3 SoC: {SoC} max: {self.max_comfort} min: {self.min_comfort} {len(self.SOC)}')
        while SoC < self.min_comfort or SoC < self.max_comfort:
            i = self.current_decay(i)
            i = min(self.max_curr,max(i,min_cur))
            p,soc = self.calculate_SoC(i,v) # calculate power, soc
            SoC += soc
            self.update_state(i,v,SoC,p)
            self.timer+=self.t_inc
        return
    def charge(self,init_SoC=0.0,fname=None):
        v = self.verbose
        time_slots = []
        if len(self.power) == 0:
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

        self.update_state(0,0,self.SOC[-1],0) # charging has ended


        # calculate the ratio of time / copies
        self.t_ratio = np.round(self.max_time/len(self.power)) # risk: divide by zero when len(power) = 0
        if self.verbose:
            print(f't ratio = max time({self.max_time})/power_len({len(self.power)}) = ',self.t_ratio)


        time_slots.append(self.time[-1])
        self.timestamps = self.generate_time_stamps()
        # self.time
        ys = [(self.SOC,'SOC (%)'),(self.power,'power (W)'),(self.currs,'current (A)'),(self.volts,'voltage (V)')] # super gross
        if fname != None:
            # self.subplot(self.time,ys,vlines=time_slots,fname=f'{fname}')
            self.plot(self.timestamps,ys[0])
            self.plot(self.timestamps,ys[1])

        d = {'time':self.timestamps,'power':self.power,'soc':self.SOC,'current':self.currs,'voltage':self.volts}

        # print(f'time: {len(self.timestamps)} power: {len(self.power)} SOC: {len(self.SOC)} currs: {len(self.currs)} volts: {len(self.volts)}')
        df = pd.DataFrame(d)
        # df.set_index('time',inplace=True)
        self.df = df
        return df.set_index('time')
    def generate_time_stamps(self):
        start = dt.fromtimestamp(self.t_start)
        end = dt.fromtimestamp(self.t_end)
        ts = pd.date_range(start=start, end=end, periods=len(self.power)).round('S') # round seconds
        return ts
    def get_soc(self,time):
        '''
            Purpose: returns the SoC at the given Epoch timestamp
            Args:
                * time: unix Epoch timestamp
            Returns: associated SoC
            Notes: Returns None if charging has not started (not plugged-in)
        '''
        soc = self.init_SoC
        try:
            record = self.get_record(time)
            soc = record['soc']
        except Exception as e:
            print(e)
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
            if self.verbose:
                print("RECORDS PROFILE\n",self.df)
            # subtract time from the starting time of the charge
            time -= self.t_start
            i = int(time/self.t_ratio) # risk: divide by zero when t_ration = 0
            if i >= len(self.df):
                record = self.df.tail(1) # could be 100% or max_comfort (if in shed mode)
            elif time <= 0:
                record = self.df.head(1)
            else:
                record = self.df.iloc[i]
        except Exception as e:
            pass # returns None as record
        if self.verbose:
            print('target record',record)
        return record
    def get_all_records(self):
        '''
            Purpose: returns log of all the records
            Args:
                * None
            Returns: log of records containing (time, power, soc, current, voltage)
            Notes: Returns None if charging has not started (not plugged-in)
        '''
        records = None
        try:
            records = self.df.set_index('time')
        except Exception:
            pass # records will be None
        return records
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
    def update_charging(self):
        # grab record at current time (if it exists)
        soc = self.init_SoC
        rec = self.get_record(time.time())
        try:
            # grab index of record
            i = rec.name
            # drop everthing past the index (for the df)
            self.df = self.df[:i]
            # grab stop index for lists
            i = len(self.df)+1
            # drop everthing past the drop index (for lists)
            self.power = self.power[:i]
            self.currs = self.currs[:i]
            self.volts = self.volts[:i]
            self.time = self.time[:i]
            self.SOC = self.SOC[:i]
            soc = rec['soc']
        except AttributeError as e:
            print(e)
            pass
        except Exception as e:
            print(tb.format_tb(e))
        # call charge with last soc
        self.charge(init_SoC=soc)
        return
    def shed(self,payload:dict):
        '''
            Purpose: modifies the setpoint
            Args:
                * payload: dict of arguments passed to the function
            Return:
                * val: dict containing return values used for CTA2045
        '''
        val = {}
        print('shedding...')
        self.min_comfort = self.min_shed
        self.max_comfort = self.max_shed
        self.state = operating_status['shed']
        self.update_charging()
        return val
    def endshed(self,payload:dict):
        '''
            Purpose: resets the setpoint
            Args:
                * payload: dict of arguments passed to the function
            Return:
                * val: dict containing return values used for CTA2045
        '''
        val = {}
        print('endshed...')
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
        val = {}
        print('loading up...')
        if not operating_status['loadup'] in self.state:
            # call endshed first
            self.endshed(payload=val)
            self.update_charging()
         # now load up
        self.state = operating_status['loadup']
        return val
    def operating_status(self,payload:dict):
        '''
            Purpose: obtain the CTA2045 operating status from the model
            Args:
                * payload: dict of arguments passed to the function
            Return:
                * val: dict containing return values used for CTA2045
        '''
        val = {}
        print('OpStatus...')
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
        val = {}
        print('CommodityRead...')
        IR0 = CA0 = CA1 = IR1 = soc = 0
        CC0 = 'electricity consumed'
        # val['commodity_code0'] = 'electricity consumed' # go with electricity consumed first
        try:
            t = time.time()
            record = self.get_record(t)
            soc = record['soc']
            IR0 = record['power']
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
        CA0 = self.max_cap * (soc - self.init_SoC)
        IR0 = CTA2045.hexify(int(IR0),length=6)
        CA0 = CTA2045.hexify(int(CA0),length=6)
        '''
        # ---------------- calculate present energy (energy take) ---------
            >> CA = max_cap(Kwh) * (1-SoC) (%)
            >> IR =  None  --> CTA2045 not used
        '''
        CA1 = self.max_cap * (1-soc)
        t = np.round(time.time(),decimals=3)
        self.commodity_log = self.commodity_log.append({'time':dt.fromtimestamp(t),
                                                        'Elect. Consumed - Cumulative (Wh)':CA0,
                                                        'Elect. Consumed - Inst. Rate (W)':IR0,
                                                        'EnergyTake - Cumulative (Wh)':CA1,
                                                        'EnergyTake - Inst. Rate (W)':IR1}
                                                        ,ignore_index=True)
        if self.verbose:
            print(f'Energy Take: {CA1} {IR1} (not supported)')
        # val['instantaneous_rate'] = CTA2045.hexify(IR0,length=6)
        CA = CTA2045.hexify(int(CA),length=6)
        CC1 = self.cta.get_code_value('commodity_code','present energy')
        CA1 = CTA2045.hexify(int(CA1),length=6)
        IR1 = CTA2045.hexify(int(IR1),length=6)
        val = {
            # ------------------------ electricity consumed measurements ---------------
            'commodity_code0':CC0,
            'cumulative_amount0':CA0,
            'instantaneous_rate0':IR0,
            # ------------------------ energy take measurements ------------------------
            'commodity_code1':CC1,
            'cumulative_amount1':CA1,
            'instantaneous_rate1':IR1,
        }
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
        self.min_comfort = self.min_cpe
        self.max_comfort = self.max_cpe
        self.state = operating_status['critical peak event']
        self.update_charging()
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
        self.min_comfort = self.min_ge
        self.max_comfort = self.max_ge
        self.state = operating_status['grid emergency']
        self.update_charging()
        return val
    def get_commodity_log(self):
        return self.commodity_log
