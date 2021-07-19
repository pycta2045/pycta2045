import json
import numpy as np


# agent's possible states
STATES = {
        0 : 'unplugged',
        1 : 'charging',
        2 : 'fully charged'
}

class generic_agent:
    def __init__(obj, in_file,time_delay=5,ramp_rate = 0,const_curr = 0, const_volt = 0,SOC = 0):
        '''
            params: 
                * file that contains information about the behavior of the agent
            return:
                None
        '''
        obj.in_file = in_file
        obj.state = 0 # starts unplugged
        # obj.delay = time_delay
        # obj.ramp_rate = ramp_rate
        # obj.const_curr = const_curr
        # obj.const_volt = const_volt
        # obj.SOC = SOC
        # obj.delta_t = time_step
        # obj.SOC_step = SOC_step
        # obj.trans_point_SOC = trans_point
        # obj.total_cap = total_cap
        return
    def read_file(self):
        '''
            params:
                None
            return:
                * contents of the json file
            function:
                * reads content of json file and returns content
        '''
        with open(self.in_file,'r') as f:
            content = json.load(f)
        self.info = content
        return content
    def get_state(self):
        '''
            params:
                None
            return:
                * current state of agent
        '''
        return STATES[self.state]
    def first_phase(self,time):
        '''
            current is kept low, volt increases
        '''
        i = 0
        while i < 5:
            t = time.pop(0)
            
            print(t)
            i+=1
        
        # SOC has reached 80%
        return time
    def second_phase(self):
        '''
            Const-curr at high until voltage reaches a point
        '''
        return
    def third_phase(self):
        '''
            volt is constant w/ curr linearly decays
        '''
        return
    def charge(self):
        '''
            charging consists of 3 phases
        '''
        time = list(range(0,100))
        time = self.first_phase(time)
        print(f'IN CHARGE: {time}')
        # self.second_phase()
        # self.third_phase()

        return
    # def get_SOC(self,current):
    #     '''
    #         calculate SOC estimate
    #     '''
    #     delta = (current/self.total_cap) * self.time_step
    #     SOC = self.SOC + (delta * 100)
    #     return SOC
