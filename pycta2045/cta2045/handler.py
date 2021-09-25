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
    def __init__(self,fname:str="CTA2045_commands.json"):
        self.cmds = {}
        path = os.path.dirname(__file__)
        try:
            with open(f'{path}/{fname}','r') as f:
                self.cmds = json.load(f)
        except Exception as e:
            print("Issue reading JSON",e)
        return
    def dump_commands(self):
        '''
            Purpose: dumps all supported CTA2045 commands (helper function).
            Args:
                * None
            Return: dictionary of supported commands.
        '''
        return self.cmds['commands']
    @staticmethod
    def hexify(value:int,length:int=1)->str:
        '''
            Purpose: Returns the hex representation of given integer (helper function).
            Args:
                * value: Integer in decimal representation.
                * length: Number of bytes to pad with (ignored if length < resulting hex representation)
            Return: hex representation.
            Note:
                * If the length of the passed value exceeds the one specified by CTA2045 standard, only the first part (up to the length specified by the startd) of the value will be taken
                * If the length is shorter, the method pads the value up to meet the required length by CTA2045 standard
        '''
        # To ensure this is hexified properly, must unhexify first.
        if isinstance(value,(int,np.integer)):
            value = hex(value)
            value = value[2:] if len(value)%2 == 0 else "0" + value[2:]
        if type(value) == str:
            value = CTA2045.parse_hex(value).split()   
        # ensure that len(value) >= length
        padded = value
        if len(value) < length:
            padded = ['00'] * (length-len(value))
            padded.extend(value)
        else:
            padded = value[:length]
        value = " ".join(list(map(lambda x: '0x'+x,padded)))
        return value
    @staticmethod
    def unhexify(value:str, combine:bool = False)->str:
        '''
            Purpose: Returns the decimal representation of given hex wrapped in str (helper function).
            Args:
                * value: Integer in hex (seperate by space -- 0x00 0x01 ...).
                * combine: produce a single output by combining all the seperated fields in `value` 
            Return: Decimal representation of the passed value 
        '''
        h = ''
        h += CTA2045.parse_hex(value)
        ret = ' '.join(map(lambda x: str(int(x,16)),h.split())) # convert to ints
        if combine:
            h = h.replace(' ','')
            ret = int(h,16)
        return str(ret)
    @staticmethod
    def parse_hex(value:str)->str:
        '''
            (Helper) Function that parses a cta2045 hex into "clean" hex (removes 0x from all the bytes)
        '''
        value = value.replace('0x','')
        value = [value[i:i+2] for i in range(0,len(value),2)]
        return " ".join(value)
    def get_default(self,key:str)->str:
        '''
            (Helper) Function that returns the default value (i.e. first value in database) for the passed key 
        '''
        ret = next(filter(None,self.cmds[key].values()))
        return ret
    def hex_sub(self,key:str,**args:dict)->str:
        '''
            (Helper) Function that returns a CTA2045 formatted hex
            Note:
                * It either uses the passed arguments to substitute for CTA2045 arguments
                * Or uses the default values from the database   
        '''
        if key in args:
            rep = args[key]
            # try to convert to approperiate value if it isn't
            try:
                if rep in self.cmds[key]:
                    rep = self.cmds[key][rep]
                else:
                    rep = self.hexify(rep,length=self.cmds[key]['length'])
            except Exception as e:
                print(e)
                pass
        else:
            rep = self.get_default(key=key)
        if 'ascii' in key:
            # convert rep from ascii -> hex -> int -> hex with proper length
            rep = int(rep.encode().hex(),16)
            rep = self.hexify(rep,length=self.cmds[key]['length'])
        return rep
    def consume_argument_dict(self,args:dict,repeated:list)->list:
        '''
           (Helper) Function that uses passed arguments to plug inplace of repeated arguments. It returns a CTA2045 formatted message that includes the passed arguments.   
        '''
        i = 0
        res = []
        while len(args)>0 or i%len(repeated) != 0 or len(res) == 0:
            target = repeated[i%len(repeated)]
            try:
                can = next(filter(lambda x: x.startswith(target),args))
                can = args.pop(can)
            except StopIteration:
                can = self.get_default(target)
            res.append(can)
            i += 1
        return res
    def to_cta(self,cmd:str,**args:dict)->str:
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
                * if repeated arguments are passed (like in commodity read response), the function extects the arguments keys to be numbered:
                    * Example: (commodity_code0, cumulative_amount0, instantaneous_rate0) for the first commodity read measurement
                        * (commodity_code1, cumulative_amount1, instantaneous_rate1) for the second
                        * ...
                        * (commodity_coden, cumulative_amountn, instantaneous_raten) for the nth measurement, and so on. 
        '''
        v = self.hexify(0)
        if 'args' in args: # drop a level
            args = args['args']
        try:
            res = self.cmds['commands'][f'{cmd}']['format']
            i = 0
            arr = res.split(' ')
            while i < len(arr): #byte in res.split(' '):
                byte = arr[i]
                if byte.isalpha():
                    k = self.cmds['codes'][f'{byte}']
                    if k== 'hash':
                        i += 1
                        continue
                    rep = self.hex_sub(k,**args)
                elif byte == '(':
                    j = arr.index(')') # grab ending index
                    repeated = arr[i+1:j]
                    repeated = list(map(lambda k: self.cmds['codes'][k],repeated))
                    repeated_len = len(repeated)
                    repeated:list = self.consume_argument_dict(args,repeated)
                    # remove the ( 
                    res = res.replace('( ','')
                    # remove the repeated elements 
                    res = res.split()
                    del res[i:i+repeated_len]
                    res = ' '.join(res)
                    byte = ')'
                    rep = ' '.join(repeated)
                else:
                    rep = byte
                res = res.replace(byte,rep)
                i += 1
            v = res
            if '#' in res:
                payload = res.split(' # ')[-1]
                payload_length = len(payload.split(' ')) - 1 # account for hash checksum (ignore it)
                res = res.replace('#',self.hexify(payload_length))
            if ' H' in res:
                res = res.split(' H')[0]
                v = f"{self.checksum(res)}"
        except Exception as e:
            raise UnknownCommandException(e)
        return v
    def checksum(self,val:str)->str:
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
    def hex_process(self,val:str)->str:
        '''
            (Helper) Function that process the hex to generate CTA2045 formatted hex (used by from_cta method).
        '''
        ret = ''
        val = val.strip().split() # trim ends and split to list
        for v in val:
            # convert to int
            i = int(v,16)
            # hexify
            h = self.hexify(i)
            ret += f' {h}'
        return ret.strip()
    def from_cta(self,val:str)->dict:
        '''
            Purpose: Translates hex representation of CTA2045 commands (0x06 0x00) to natural language representation (link-layer ack)
            Args:
                * val: a hex representation of a CTA2045 command
            Return: Dictionary of what the command represents.
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
            print(tb.format_tb(e))
            pass
        return response
    def consume_argument(self,arg:dict, pos:int, length:int, msg:str, form:str, key:str)->str:
        '''
            (Helper) Function that returns translates a specific (in a specific position and length) argument in the given message (used indirectly by from_cta -- through extract_args).
        '''
        value = msg[pos:pos+length]
        # get associated key
        value = " ".join(value)
        try:
            value = next(k for k,v in self.cmds[arg].items() if v.upper() == value.upper())
        except Exception as e:
            arguments = {}
            func = None
            combine = False
            # change this into being a seperated hex
            if 'ascii' in arg:
                value = self.unhexify(value,combine=length<=2)
                # clean string from unprintable characters
                value = ' '.join(filter(lambda x: 32<=int(x,16)<=126,value.split()))
                value = ''.join(map(lambda x: chr(int(x)),value.split())).strip() # apply the function on
            else:
                value = self.unhexify(value,combine=True)
        return value
    def extract_args(self,cmd:str,val:str)->dict:
        '''
            (Helper) Function that uses the passed value (CTA2045 formatted hex and command type) and extracts expected arguments from it (used by from_cta). 
        '''
        # get command name
        key = cmd['command']
        cmd['args'] = {}
        # get arguments
        form = cmd['format'].split()
        i = j = 0
        while i < len(form) and j < len(val):
            if form[i] == '(':
                i += 1 # ignore the ( symbol
                repeat = []
                start = i
                end = form.index(')')
                repeat = form[start:end]
                # repeatedly extract arguments until end of val
                num = entry = 0
                while j < len(val) and len(val) - j > len(repeat):    
                    arg = self.cmds['codes'][repeat[num%len(repeat)]]
                    length = int(self.cmds[arg]['length'])
                    value = self.consume_argument(arg,j,length,val,form,key)
                    if f'{arg}{entry}' in cmd['args']:
                        entry += 1
                        cmd['args'][f'{arg}{entry}'] = value
                    else:
                        cmd['args'][f'{arg}{entry}'] = value
                    j += length
                    num += 1
                i += num + 1 # ignore the ) symbol
                continue
            if form[i].isalpha() and form[i] != 'H':
                arg = self.cmds['codes'][form[i]]
                length = int(self.cmds[arg]['length'])
                value = self.consume_argument(arg,j,length,val, form, key)
                cmd['args'][arg] = value
                j += length -1 
            i += 1
            j += 1
        return cmd
    def complement(self,command:str)->list:
        '''
            Purpose: returns the complement of passed command (if supported only)
            Args:
                * cmd (string): desired command to find complement of
            Return: complement of passed command
            Note:
                * Can be used by devices to follow CTA2045 protocol (i.e. should send an ACK followed by App ACK)
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
    def get_code_value(self,key:str=None,code:str=None)->str:
        '''
            Purpose: returns the value for the requested code.
            Args:
                * key (string): desired key code to search in.
                * code (string): desired code field to find the value of
            Return: value of the given code field (string of CTA2045 hex)
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
    def set_supported(self,command:str,value: bool)->bool:
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
    def is_valid(self,msg:str)->bool:
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
    def from_cta_bytes(self,encoded_bytes:bytes)->dict:
        '''
            Purpose: function that translates CTA2045 bytes into a dictionary of corresponding CTA2045 command.
            Args:
                * encoded_bytes: CTA2045 bytes
            Returns: dictionary containing information translated corresponding command 
        '''
        # convert to str
        assert type(encoded_bytes) == bytes, 'argument must be of type bytes'
        s = bytes.decode()
        s = s.replace('/',' ').strip()
        # hexify
        return self.from_cta(s)
    def to_cta_bytes(self,cmd:str,**args:dict)->bytes:
        '''
            Purpose: function that returns a CTA2045 command bytes (uses to_cta before converting to bytes).
            Args:
                * cmd (string): desired CTA2045 command
                * args (dict): optional arguments that are used in the translation process
            Returns: bytes of the CTA2045 command ready to be sent via serial com port
        '''
        byte = b''
        # convert to command
        cta = self.to_cta(cmd,args=args)
        assert cta != None, 'Error translating command'
        arr = cta.split(' ')
        for i in arr:
            # convert to int from hex
            byte += int(i,16).to_bytes(length=1,byteorder='big',signed=False)
        # hexify
        return byte