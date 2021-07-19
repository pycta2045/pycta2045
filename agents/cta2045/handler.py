import json
import os
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
    def get_hex(self,cmd):
        v = hex(0)
        try:
            v = f"{self.cmds['op code']} {self.cmds[cmd]}"
        except Exception as e:
            print(e)
        return v
    def get_key(self,val):
        key = None
        for k,v in self.cmds.items():
            if v == val:
                key = k
        return key