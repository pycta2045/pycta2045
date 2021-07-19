import json
import os


# @TEST:
# 1. create basic message & test length against combined length given from dict
# 2. create data-link message & test length against combined length given from dict
# 3. acks/naks should be 2 bytes only

class command_handler:
    def __init__(self,fname="CTA2045_commands.json"):
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
    def to_cta(self,cmd):
        # TODO: 
        # 1. query MsgType from dict
        # 2. query msg from dict
        # 3. call checksum on msg

        v = hex(0)
        try:
            v = f"{self.cmds['op code']} {self.cmds[cmd]}"
        except Exception as e:
            print(e)
        return v
    def from_cta(self,hex):
        key = None
        for k,v in self.cmds.items():
            if v == val:
                key = k
        return key