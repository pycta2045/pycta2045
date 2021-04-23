import json
class command_handler:
    def __init__(self,fname="cta2045/CTA2045_commands.json"):
        self.cmds = {}
        try:
            print("----------")
            with open(fname,'r') as f:
                self.cmds = json.load(f)            
        except Exception as e:
            print(e)
        return
    def dump_commands(self):
        return self.cmds
    def get(self,cmd):
        v = hex(0)
        try:
            v = self.cmds['op code'] + self.cmds[cmd]
        except Exception as e:
            print(e)
        return v