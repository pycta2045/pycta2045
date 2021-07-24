from agents.cta2045.handler import CTA2045
from agents.com.handler import COM



port = 'COM6'
com = COM()
cta = CTA2045()

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
com.send(cta.to_cta('nak'))
x = com.recv(length=2)
print(x)
