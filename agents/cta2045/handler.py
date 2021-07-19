import json
import os


# @TEST:
# 1. create basic message & test length against combined length given from dict
# 2. create data-link message & test length against combined length given from dict
# 3. acks/naks should be 2 bytes only

class command_handler:
    def __init__(self,fname="CTA2045_commands_simple.json",max_payload=4096):
        self.cmds = {}
        path = os.path.dirname(__file__)
        try:
            with open(f'{path}/{fname}','r') as f:
                self.cmds = json.load(f)            
        except Exception as e:
            print(e)
        return
    def dump_commands(self):
        return self.cmds
    def to_cta(self,cmd,*args):
        # TODO: 
        # 1. query MsgType from dict
        # 2. query msg from dict
        # 3. call checksum on msg
        v = '0x{:02x}'.format(0)
        try:
            res = self.cmds[f'{cmd}']
            if ' D ' in res: # duration (default to unknwon duration)
                duration = args[0] if len(args) >=1 else "0x00"
                res = res.replace(' D ',f' {duration} ')
            elif 'M' in res: # default to max payload
                res = res.replace('M',self.cmds['max payload lengths'][f'{max_payload}'])
            elif 'R' in res:
                reason = "none"
                if len(args) >=1 and args[0] in self.cmds['nak reasons']:
                    reason = self.cmds['nak reasons'][args[0]]
                res = res.replace('R',reason)
            v = res
            if 'C C' in res:
                res = res.split(' C C')[0]
                v = f"{self.checksum(res)}" 
                # v = 0
        except Exception as e:
            print(e)
        return v
    

    def checksum(self,val):
        c1 = int("0xaa",16)
        c2 = int("0x00",16)
        for byte in val.split(' '):
            # convert to int
            # print(byte)
            i = int(byte.strip(),16)
            c1 = (c1 + i) % 255
            c2 = (c1 + c2) % 255
        msb = 255 - ((c1 + c2) % 255)
        lsb = 255 - ((c1 + msb) % 255) 
        val = f"{val} {'0x{:02x}'.format(msb)} {'0x{:02x}'.format(lsb)}"
        print(val)
        return val
    def from_cta(self,hex):
        key = None
        for k,v in self.cmds.items():
            if v == val:
                key = k
        return key