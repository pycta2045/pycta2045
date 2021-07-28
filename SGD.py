from agents.cta2045.handler import CTA2045
from agents.com.handler import COM,TimeoutException



class SGD:
    port = 'COM6'
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
        print(f'sending {cmd}...')
        if len(args) >0:
            print('\t args: ',args)
        c =  self.cta.to_cta(cmd,args= args)
        self.com.send(c)
        try:
            if 'ack' in cmd or 'nak' in cmd:
                res = True
            else:
                res = self.recv()
            if type(res) == dict:
                print('\treceived: ',res['command'])
                for k,v in res['args'].items():
                    print(f'\t{k}\t{v}')
        except Exception as e:
            print(e)
        return res

    def setup(self):
        res = None
        # iMTSQ
        cmd = 'intermediate MTSQ'
        res = self.send(cmd)
        if res != None and 'command' in res and res['command'] == 'ack':
            intermediate = True

        # dMTSQ
        cmd = 'data-link MTSQ'
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
                last_command = res['op1']
                print(res['command'])
                for k,v in res['args'].items():
                    print(f'\t{k} = {v}')
                complement = self.cta.complement(res['command'])
                if complement != None:
                    self.send('ack')
                    if 'type' in res and res['type']['str'] == 'basic' and not "response" in complement:
                        self.send('app ack',last_opcode=last_command)
                    if "response" in complement:
                        self.send(complement)
                elif complement==None:
                    pass
                else:
                    self.send('nak', nak_reason='unsupported')
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
