import json
import os

class CTA2045:
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
        '''(helper function)
            Purpose: dumps all supported CTA2045 commands (helper function).
            Args:
                * None
            Return: dictionary of supported commands.
        '''
        return self.cmds['commands']
    def hexify(self,val):
        '''(helper function)
            Purpose: Returns the hex representation of given integer (helper function).
            Args:
                * val: Integer in decimal representation.
            Return: hex representation.
        '''
        return '0x{:02x}'.format(val)
    def to_cta(self,cmd,**args):
        '''
            Purpose: Translates natural language commands like shed, endshed, commodity read, etc.  to corresponding hex value representation as specified by CTA2045-B.
            Args:
                * cmd: command (shed,endshed,....).
                * args: dictionary to arguments the command take. For example, shed, endshed and loadup take duration as a an argument.
            Return: hex representation ready to be used (sent to SGD or UCM).
            Notes:
                * if no arguments are passed, the function uses the defaults.
                    * first value in the corresponding key within CTA2045_commands.json.
                * it uses Fletcher’s 16-bit 1’s complement as a hashing function as specified by CTA2045-B.
                    * This DOES NOT provide security. In fact, CTA2045-B does not address security measures at all.
        '''
        v = self.hexify(0)
        try:
            res = self.cmds['commands'][f'{cmd}']['format']
            for byte in res.split(' '):
                if byte.isalpha():
                    k = self.cmds['codes'][f'{byte}']
                    if k== 'hash':
                        continue
                    if k in args:
                        rep = args[k]
                    else:
                        rep = list(self.cmds[f'{k}'].values())[0]
                    res = res.replace(byte,rep)
            v = res
            if '#' in res:
                payload = res.split(' # ')[-1]
                payload_length = len(payload.split(' ')) - 1 # account for hash checksum (ignore it)
                res = res.replace('#',self.hexify(payload_length))
            if ' H' in res:
                res = res.split(' H')[0]
                v = f"{self.checksum(res)}"
        except Exception as e:
            print(e)
        return v
    def checksum(self,val):
        '''
            Purpose: Hashes the passed argument using Fletcher’s checksum algorithm
            Args:
                * val: a hex representation of a CTA2045 command
            Return: hex representation with checksum appended at the end (last 2 bytes)
        '''
        c1 = int("0xaa",16)
        c2 = int("0x00",16)
        for byte in val.split(' '):
            i = int(byte.strip(),16)
            c1 = (c1 + i) % 255
            c2 = (c1 + c2) % 255
        msb = 255 - ((c1 + c2) % 255)
        lsb = 255 - ((c1 + msb) % 255)
        val = f"{val} {self.hexify(msb)} {self.hexify(lsb)}"
        return val
    def from_cta(self,val):
        '''
            Purpose: Translates hex representation of CTA2045 commands (0x06 0x00) to natural language representation (link-layer ack)
            Args:
                * val: a hex representation of a CTA2045 command
            Return: String of what the command represents.
            Notes:
                * This function uses CTA2045_commands.json. So it is limited to only supported commands in the JSON file.
                * If the command is not supported, it returns None as an output.
        '''
        d = {}
        key = None
        h = 0
        val = val.split(' ')
        l = len(val)
        for k,v in self.cmds['commands'].items():
            t = v['type']
            op1 = v['op1']
            op2 = v['op2']
            if l <=2:
                # only check 1st part of type
                t1,t2 = t.split(' ')
                if t2.isalpha():
                    t2 = val[-1]

                if ' '.join([t1,t2]) == ' '.join(val[:2]):
                    key = k
                    break
            elif l<=6:
                # only check type (could be MTSQ)
                if t in ' '.join(val) and op1 == 'None' and op2 == 'None':
                    key = k
                    break
            else:
                # check type & opcodes
                vop1 = val[4]
                vop2 = val[5]
                if op2.isalpha():
                    op2 = vop2
                if ' '.join(val[:2]) == t and op1 == vop1 and op2 == vop2:
                    key = k
                    break
        # get command name
        d['command'] = key
        d['args'] = {}
        # get arguments
        if key in self.cmds['commands']:
            form = self.cmds['commands'][key]['format'].split()
            i = j = 0
            while i < len(form) and j < len(val):
                if form[i].isalpha():
                    arg = self.cmds['codes'][form[i]]
                    length = int(self.cmds[arg]['length'])
                    value = val[j:j+length]
                    d['args'][arg] = value
                    j += length - 1
                i += 1
                j += 1

        return d
    def complement(self,cmd):
        '''
            Purpose: returns the complement of passed command
            Args:
                * cmd (string): desired command to find complement of
            Return: complement of passed command
        '''
        comd_complement  = None
        if "request" in cmd:
            cmd_complement = cmd.replace("request","response")
        return cmd_complement