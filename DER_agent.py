from agents.scpi.handler import SCPI
import sys
import argparse
from agents.gen_agent import generic_agent
from agents.cta2045.handler import command_handler
from agents.com.handler import COM



# measure everything
# something to recv



# scpi = SCPI()
# r = scpi.send('lock screen')
# DER_agent = generic_agent('file.json')
# print(DER_agent.get_state())

# print(f'shed: {shed}')
# # DER_agent.charge()

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

scpi = SCPI()
(s,r) = scpi.send("lock screen",recv=True)
print(r)
(s,r) = scpi.send("identify",recv=True)
print(r)
r = scpi.send_command("SYST:LOC\n")
print(r)
