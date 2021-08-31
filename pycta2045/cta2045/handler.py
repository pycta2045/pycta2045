import json, os, traceback as tb, numpy as np

class UnsupportedCommandException(Exception):
    '''
        Used to indicate that the given command is unsupported
    '''
    def __init__(self,msg):
        self.message = msg
        super().__init__(self.message)
class UnknownCommandException(Exception):
    '''
        Used to indicate that the given command is unknown
    '''
    def __init__(self,msg):
        self.message = msg
        super().__init__(self.message)

class CTA2045:
    def __init__(self,fname="CTA2045_commands.json"):
        self.cmds = {}
        path = os.path.dirname(__file__)
        try:
            with open(f'{path}/{fname}','r') as f:
                self.cmds = json.load(f)
        except Exception as e:
            print("Issue reading JSON",e)
        return
    def dump_commands(self):
        '''(helper function)
            Purpose: dumps all supported CTA2045 commands (helper function).
            Args:
                * None
            Return: dictionary of supported commands.
        '''
        return self.cmds['commands']
    @staticmethod
    def hexify(value,length=1):
        '''(helper function)
            Purpose: Returns the hex representation of given integer (helper function).
            Args:
                * value: Integer in decimal representation.
                * length: Number of bytes to pad with (ignored if length < resulting hex representation)
            Return: hex representation.
        '''
        value = hex(value)
        value = value[2:] if len(value)%2 == 0 else "0" + value[2:]
        value = [value[i:i+2] for i in range(0,len(value),2)]
        # ensure that len(value) >= length
        padded = value
        if len(value) < length:
            padded = ['00'] * (length-len(value))
            padded.extend(value)
        value = " ".join(list(map(lambda x: '0x'+x,padded)))
        return value
    @staticmethod
    def unhexify(value, func: callable = int):
        '''(helper function)
            Purpose: Returns the decimal representation of given hex (helper function).
            Args:
                * value: Integer in hex (seperate by space -- 0x00 0x01 ...).
                * length: Number of bytes to convert
            Return: decimal representation.
        '''
        h = '0x'
        h += parse_hex(value).replace(' ','')
        return int(h,16)

    @staticmethod
    def parse_hex(value):
        value = value.replace('0x','')
        return value

    def to_cta(self,cmd,**args):
        '''
            Purpose: Translates natural language commands like shed, endshed, commodity read, etc.  to corresponding hex value representation as specified by CTA2045-B.
            Args:
                * cmd: command (shed,endshed,....).
                * args: dictionary of arguments the command take. For example, shed, endshed and loadup take duration as a an argument.
            Return: hex representation ready to be used (sent to SGD or UCM).
            Notes:
                * if no arguments are passed, the function uses the defaults.
                    * first value in the corresponding key within CTA2045_commands.json.
                * it uses Fletcher’s 16-bit 1’s complement as a hashing function as specified by CTA2045-B.
                    * This DOES NOT provide security. In fact, CTA2045-B does not address security measures at all.
        '''
        v = self.hexify(0)
        if 'args' in args: # drop a level
            args = args['args']
        try:
            res = self.cmds['commands'][f'{cmd}']['format']
            for byte in res.split(' '):
                if byte.isalpha():
                    k = self.cmds['codes'][f'{byte}']
                    if k== 'hash':
                        continue
                    if k in args:
                        rep = args[k]
                        # convert to approperiate value if it isn't
                        if rep in self.cmds[k]:
                            rep = self.cmds[k][rep]
                    else:
                        rep = list(self.cmds[f'{k}'].values())[0]
                    if 'ascii' in k: 
                        # convert rep from ascii -> hex -> int -> hex with proper length
                        rep = int(rep.encode().hex(),16)
                        rep = self.hexify(rep,length=self.cmds[k]['length'])
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
    def hex_process(self,val):
        ret = ''
        val = val.strip() # trim ends
        val = val.split() # strip to list
        for v in val:
            # convert to int
            i = int(v,16)
            # hexify
            h = self.hexify(i)
            ret += f' {h}'
        return ret.strip()
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
        val = self.hex_process(val)
        response = None
        key = None
        try:
            val=val.lower()
            val = val.split(' ')
            l = len(val)
            for k,v in self.cmds['commands'].items():
                t = v['type']['hex'].lower()
                vlen = len(v['format'].split())
                op1 = v['op1'].lower()
                op2 = v['op2'].lower()
                if l ==2 and vlen == l:
                    # only check 1st part of type
                    t1,t2 = t.split(' ')
                    if t2.isalpha():
                        t2 = val[-1]
                    if ' '.join([t1,t2]) == ' '.join(val[:2]):
                        key = k
                        break
                elif l>=4 and l <=6:
                    # only check type (could be MTSQ)
                    if t in ' '.join(val) and op1 == 'none' and op2 == 'none':
                        key = k
                        break
                elif l > 6:
                    # check type & opcodes
                    vop1 = val[4]
                    vop2 = val[5]
                    if op2.isalpha():
                        op2 = vop2
                    if ' '.join(val[:2]) == t and op1 == vop1 and op2 == vop2:
                        key = k
                        break
            response = self.cmds['commands'][key]
            response['command'] = key
            response = self.extract_args(response,val)
            # check if it is supported
            if not response['supported']:
                val = key
                raise UnsupportedCommandException(key)
        except (KeyError,TypeError) as e:
            raise UnknownCommandException(f'{val}')
        except UnsupportedCommandException as e:
            raise UnsupportedCommandException(val) # pass command
        except Exception as e:
            # unable to translate msg (unknown) -- return None
            print(tb.format_tb())
            pass
        return response
    def extract_args(self,cmd,val):
        # get command name
        key = cmd['command']
        cmd['args'] = {}
        # get arguments
        #if key in self.cmds['commands']:
        form = cmd['format'].split()
        i = j = 0
        while i < len(form) and j < len(val):
            if form[i].isalpha() and form[i] != 'H':
                arg = self.cmds['codes'][form[i]]
                length = int(self.cmds[arg]['length'])
                value = val[j:j+length]
                # get associated key
                value = " ".join(value)
                try:
                    value = next(k for k,v in self.cmds[arg].items() if v.upper() == value.upper())
                except Exception as e:
                    if 'ascii' in arg:
                        value = '' .join(map(chr,self.parse_hex(value).split()))
                    else:
                        value = self.unhexify(value)
                cmd['args'][arg] = value
                j += length - 1
            i += 1
            j += 1
        return cmd
    def complement(self,command):
        '''
            Purpose: returns the complement of passed command (if supported only)
            Args:
                * cmd (string): desired command to find complement of
            Return: complement of passed command
        '''
        cmd_complement = []
        try:
            if not 'ack' == command and not 'nak' == command:
                cmd = self.cmds['commands'][command]
                # find appropriate ack type
                t = cmd['type']['str']
                cmd_complement.append('ack')
                if t == 'basic' and not 'request' in command:
                    cmd_complement.append('app ack')
                # find complement
                if 'request' in command:
                    comp = command.replace('request','response')
                    if comp in self.cmds['commands'].keys():
                        cmd_complement.append(comp)
        except Exception as e:
            # command not found or unable to response -- send a nak
            cmd_complement = ['nak']
        return cmd_complement
    def get_code_value(self,key=None,code=None):
        '''
            Purpose: returns the value for the requested code.
            Args:
                * key (string): desired key code to search in.
                * code (string): desired code field to find the value of
            Return: value of the given code field
            NOTE:
                * returns 0 if code was not found
                * example:
                    * get_code_value('commodity_code','present energy') returns the 0x80 as 'present energy' value for commodity_code is 0x80
        '''
        value = self.hexify(0)
        try:
            codes = self.cmds['codes'].values()
            key = next(v for v in codes if v.upper() == key.upper())
            value = self.cmds[key][code.lower()]
        except Exception:
            # do nothing (value is still 0x00)
            pass
        return value
    def set_supported(self,command,value: bool):
        '''
            Purpose: sets the `supported` field for the passed command to the passed bool value
            Args:
                * command: target command
                * value: boolean value to assign to the `supported` field
            Return:
                * True if the value has be set
                * False otherwise
        '''
        try:
            assert(type(value) == bool)
            self.cmds['commands'][command]['supported'] = value
            return True
        except Exception as e:
            print(f'Failed to set the supported field for: {command}: ',e)
            pass
        return False
    def is_valid(self,msg):
        '''
            Purpose: checks if the passed message is a valid CTA msg (supported CTA2045 msgs only)
            Args:
                * msg (string): desired msg to check
            Return:
                * True: msg is a valid CTA2045 msg and supoorted
                * False: msg is not valid CTA2045 or not supported
        '''
        valid = False
        if len(msg) > 2:
            # checksum is valid?
            unchecked_data = msg[:-2]
            checked_data = self.checksum(" ".join(unchecked_data)).split(" ")
            if np.array_equal(msg,checked_data):
                valid = True
        else: # could be link ack/nak
            if self.from_cta(" ".join(msg)) != None:
                valid = True
        return valid
    def from_cta_bytes(self,encoded_bytes):
        # convert to str
        assert type(encoded_bytes) == bytes, 'argument must be of type bytes' 
        s = bytes.decode()
        s = s.replace('/',' ').strip()
        # hexify
        return self.from_cta(s)
    def to_cta_bytes(self,cmd:str):
        byte = b''
        # convert to command
        cta = self.to_cta(cmd)
        assert cta != None, 'Error translating command'
        arr = cta.split(' ')
        for i in arr:
            # convert to int from hex
            byte += int(i,16).to_bytes(length=1,byteorder='big',signed=False)
        # hexify
        return byte
