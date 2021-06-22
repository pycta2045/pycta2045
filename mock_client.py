from multiprocessing.connection import Client
import argparse
import subprocess
from agents.cta2045.handler import command_handler as cta2045

def prompt(cta_cmds):
    choices = {
        0: 'shed',
        1: 'endshed',
        2: 'loadup',
        3: 'quit',
    }
    choice = -1
    while choice < 0 and choice != 3:
        print(10*'---')
        for k,v in choices.items():
            print(f'{k}: {v}')
        try:
            choice = int(input('choice: '))
        except Exception as e:
            print('invalid choice!')
            choice = -1
    if choice == 3:
        return (choices[choice],choice)
    return (cta_cmds.get_hex(choices[choice]),choice)



def main():
    parser = argparse.ArgumentParser(description='Process program args.')
    parser.add_argument('-p', type=str, help='port to use',default='/dev/ttyS5')

    cta = cta2045()
    args = parser.parse_args()
    port = int(args.p)


    # start up DER agent
    print('starting DER agent...')
    # run DER agent as subprocess w/ local option on
    # child = subprocess.Popen(['python3','DER_agent.py','-l 1',f'-p {port}'])
    try:
        addr = ('localhost',port)
        conn = Client(addr,authkey=b'pass')
        c = -1
        while c != 3:
            (msg,c) = prompt(cta)
            conn.send(msg)
        conn.send('quit')
        conn.close()
    except Exception as e:
        print('failed')
        print(e)
        # child.terminate()
main()