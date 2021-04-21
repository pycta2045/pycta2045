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

# def command(op,off):
#     op = [hex(x) for x in op]
#     #op = ' '.join(op)
#     off = [hex(x) for x in off]
#     #off = ' '.join(off)
#     return ' '.join(op + off).upper()

# print(command(op_code,shed))
# print(command(op_code,loadup))
# print(command(op_code,endshed))
