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

scpi = SCPI(addr='192.168.0.149')
(s,r) = scpi.send("lock screen",recv=True)
print(r)
(s,r) = scpi.send("identify",recv=True)

curr = 0.75
r= scpi.send("set current",args=[str(curr)])
print(r)
(s,r) = scpi.send("get current",recv=True)
print(f"did current change? {r}")

'''

print(r)
r = scpi.send_command("SYST:LOC\n")
print(r)
charger = charger(max_volt=30,max_curr=0,max_cap=240,min_comfort=0.85,max_comfort=0.95,rampup_time=1, decay_rate=.9)
charger.shed()
ret = charger.charge()
#for i in range(100):
    #ret = charger.charge(init_SoC=ret['soc'].iloc[-1])
ret = charger.charge(init_SoC=ret['soc'].iloc[-1],fname='plot1')
print(len(ret))
'''

