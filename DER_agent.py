from agents.scpi.handler import SCPI
import sys
import argparse
from agents.gen_agent import generic_agent
from agents.cta2045.handler import command_handler
from agents.com.handler import COM
from agents.charger.charger import charger



# measure everything
# something to recv



# scpi = SCPI()
# r = scpi.send('lock screen')
# DER_agent = generic_agent('file.json')
# print(DER_agent.get_state())

# print(f'shed: {shed}')
# DER_agent.charge()


parser = argparse.ArgumentParser(description='Process program args.')
parser.add_argument('-p', type=str, help='port to use',default='/dev/ttyS5')
parser.add_argument('-m', type=bool, help='mode {True: listen, False: send}',default=False)
# parser.add_argument('-c', type=str, help='command to send',default='shed')




'''
args = parser.parse_args()
port = args.p
# cmd = args.c
listen = args.m

print(listen)
com = COM(port)
cta = command_handler(fname="agents/cta2045/CTA2045_commands.json")
cmds = cta.dump_commands()
    
if listen:
    # while input() != 'q':
    r = com.recv()
    print(f'recv: {r}')
else:
    shed = cta.get("shed")
    com.send(shed)
    print(f'sent: {shed}')
    # r = com.recv()

'''


charger = charger(max_volt=240,max_curr=30,max_cap=240,min_comfort=0.85,max_comfort=0.95)
charger.shed()
ret = charger.charge()

scpi = SCPI()

(s,r) = scpi.send("lock screen")
for i in ret.iloc:
    c = i['current']
    (s,r)= scpi.send("current",args=[str(c)])
    res = scpi.send("current",cmd_type=1)
    print(f'cmd: curr {c}  --  query: {res}')


(s,r) = scpi.send("unlock screen")
print(r)
