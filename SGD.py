from agents.cta2045.handler import CTA2045
from agents.com.handler import COM,TimeoutException
import sys

class SGD:
    cta = CTA2045()
    com = COM(checksum=cta.checksum,transform=cta.hexify)
    def __init__(self):
        # initialize the values
        pass

    def recv(self):
        res = self.com.recv()
        ret = self.cta.from_cta(res)
        return ret

    def send(self,cmd,**args):
        res = None
        c =  self.cta.to_cta(cmd,args= args)
        self.com.send(c)
        print(f'=-> sent {cmd}')
        if len(args) >0:
            print('\twith args: ',args)
        try:
            if 'ack' in cmd or 'nak' in cmd:
                res = True
            else:
                res = self.recv()
            if type(res) == dict:
                print('<-= received: ',res['command'])
                for k,v in res['args'].items():
                    print(f'\t{k}\t{v}')
        except Exception as e:
            print(e)
        return res
    def setup(self):
        res = None
        # iMTSQ
        cmd = 'intermediate mtsq'
        res = self.send(cmd)
        if res != None and 'command' in res and res['command'] == 'ack':
            intermediate = True

        # dMTSQ
        cmd = 'data-link mtsq'
        res = self.send(cmd)
        if res != None and 'command' in res and res['command'] == 'ack':
            data_link = True

        # MPQ
        cmd = 'max payload request'
        res = self.send(cmd)
        return
    def start(self):
        last_command = '0x00'
        # always on waiting mode
        while True:
            try:
                res = self.recv()
                if res != None:
                    last_command = res['op1']
                    print(res['command'])
                    for k,v in res['args'].items():
                        print(f'\t{k} = {v}')
                    res = res['command']
                complement = self.cta.complement(res)
                for cmd in complement:
                    if cmd == 'app ack':
                        self.send(cmd, last_opcode=last_command)
                    elif cmd == 'nak':
                        self.send(cmd,nak_reason='unsupported')
                    else:
                        self.send(cmd)
            except TimeoutException as e:
                # nothing was received from UCM
                continue
            except Exception as e:
                print(e)
                continue

# SET UP
sgd = SGD()
sgd.setup()
sgd.start()
