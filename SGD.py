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

#com.send(cta.to_cta('ack'))

'''
packet = bytearray()
data = cta.to_cta('ack').split(' ')
data = list(map(lambda x:int(x,16),data))
print(data)
packet.extend(data)
#packet.extend(hex(cta.to_cta('ack').split(' '))
print(packet)
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
