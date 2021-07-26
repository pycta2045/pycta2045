from agents.cta2045.handler import CTA2045
from agents.com.handler import COM

# @TODO:
# 1. update recv function in com/handler.py
# * make it use nonblocking recv
# * pull 2 bytes at a time from serial com
# * add argument (function type) :
# *    use to deceide when to flush (function should be checksum)
# *    use in_waiting buffer to decide when to call flush
# 2. test new recv function behavior


port = 'COM6'
cta = CTA2045()
com = COM(checksum=cta.checksum,transform=cta.hexify)

intermeidate = False
data_link = False

def recv():
    res = com.recv()
    ret = cta.from_cta(res)
    return ret

def send(cmd,**args):
    print(f'sending {cmd}...')
    c = cta.to_cta(cmd,args=args)
    com.send(c)
    if cmd == 'ack' or cmd == 'nak':
        res = True
    else:
        res = recv()
    if type(res) == dict:
        print('\treceived: ',res['command'])
        for k,v in res['args'].items():
            print(f'\t{k}\t{v}')
    return res

def setup():
    res = None
    # iMTSQ
    cmd = 'intermediate MTSQ'
    res = send(cmd)
    if res == 'ack':
        intermediate = True

    # dMTSQ
    cmd = 'data-link MTSQ'
    res = send(cmd)
    if res == 'ack':
        data_link = True

    # MPQ
    cmd = 'max payload request'
    res = send(cmd)
    if res == 'ack':
        res = recv()
        #print('\tpayload: ',res)
        send('ack')

    return

# SET UP
setup()
x = send('operating status response',args={'op_state_code':'idle normal'})

send('ack')

'''
while True:

    x = com.recv()
    cmd = cta.from_cta(x)
    print("received command: ",cmd)
    print("sending ack...",com.send(cta.to_cta('ack')))
    res = cta.complement(cmd)
    print("sending complement...",res)
    if not res == None:
        com.send(cta.to_cta(res))
        x = com.recv()
'''

