from agents.scpi.handler import SCPI
import sys
import argparse
from agents.gen_agent import generic_agent
from agents.cta2045.handler import command_handler as cta_handler
from agents.com.handler import COM
from agents.charger.charger import charger
from multiprocessing.connection import Listener # used for local communication


# measure everything
# something to recv



# scpi = SCPI()
# r = scpi.send('lock screen')
# DER_agent = generic_agent('file.json')
# print(DER_agent.get_state())

# print(f'shed: {shed}')
# DER_agent.charge()

'''
def process_command(cmd,cta2045_cmds):
    # cmd: cta2045 command
    cmd = cmd.split(' ')
    # ignore op code & focus on command code
    cmd = ' '.join(cmd[4:])
    cmd = cta2045_cmds.get_key(cmd)

    # @TODO: act on cta2045 commands to create profile
    return cmd


def main():
    parser = argparse.ArgumentParser(description='Process program args.')
    parser.add_argument('-p', type=str, help='port to use',default='/dev/ttyS5')
    # parser.add_argument('-m', type=bool, help='mode {True: listen, False: send}',default=False)
    parser.add_argument('-l', type=int, help='local DCM mode (False = 0, True > 0)',default=0)
    # parser.add_argument('-c', type=str, help='command to send',default='shed')



    args = parser.parse_args()
    port = args.p
    local = args.l
    local = True if local > 0 else False

    print(local)
    if local:
        # run a local version (listen to local port for DCM commands)
        addr = ('localhost',int(port))
        listener = Listener(addr,authkey=b'pass')
        conn = listener.accept()
        print('connection started...')
        cta2045_cmds = cta_handler()
        while True:
            cmd = conn.recv() # CTA2045 command + connection command (quit)
            if cmd == 'quit':
                print('closing...')
                conn.close()
                break
            # process CTA2045 command
            process_command(cmd,cta2045_cmds)
        listener.close() # close connection
    else:
        # use COM to module to handle serial communication 
        # com = COM(port)
        return
    return
'''

'''
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

scpi = SCPI()
(s,r) = scpi.send("lock screen",recv=True)
print(r)
(s,r) = scpi.send("identify",recv=True)

curr = 0.75
r= scpi.send("set current",args=[str(curr)])
print(r)
(s,r) = scpi.send("get current",recv=True)
print(f"did current change? {r}")


print(r)
r = scpi.send_command("SYST:LOC\n")
print(r)

charger = charger(max_volt=30,max_curr=20,max_cap=240,min_comfort=0.85,max_comfort=0.95,decay_rate=1.1,rampup_delay=1)
charger.shed()
ret = charger.charge(fname='plot')
ret = charger.charge(init_SoC=ret[-1],fname='plot1')
print(len(ret))

if __name__=="__main__":
    main()
    exit()
# main()
'''
com = COM()
print(help(com))

