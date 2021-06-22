import socket
import time
import pandas as pd
import json
import os


timeout = 1 # timeout len used in connection
port = 5025 # port used for connection
buf_sz = 1024 # size of buffer used in recv

class SCPI:
    def __init__(self,addr = "192.168.0.153",commands_file='commands.json',log_file='log'):
        '''
            params:
                * addr: address of server to connect to
                * commands_file: path to SCPI commands file
                * log_file: desired name of log file
            return:
                None
        '''
        self.addr = addr
        path = os.path.dirname(__file__)
        print(f"connecting to {addr}:{port}...")
        self.soc = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.soc.settimeout(timeout) # time out in secs
        self.soc.connect((addr,port))
        print("connected!")
        with open(f'{path}/{commands_file}','r') as f:
            commands = json.load(f)
        self.commands = commands
        self.log_file = log_file+'.csv'
        return
    def log(self,l):
        l['time'] = int(time.time()) 
        print(l)
        df = pd.DataFrame(l)
        df.set_index('time',inplace=True)
        df.to_csv(self.log_file,mode='a',header=False)
        return

    def send_command(self,cmd,recv=False):
        '''
            sends a command through the socket
        '''
        self.soc.send(f"{cmd}\n".encode())
        if recv:
            ret = self.soc.recv(buf_sz).decode()
        else:
            ret = True
        return ret
    def send(self,cmd,args=None,recv=False):
        status = False
        try:
            cmd = self.commands['common'][cmd]
            if not args is None:
                cmd = f"{cmd} {' '.join(args)}"
            res = self.send_command(cmd,recv) # send command 
            status = True
        except Exception as e:
            res = e
        self.log({'command':[cmd],'response':[res],'status':[status]})
        return (status,res)
    # ================= other commands functions ================

print(__name__)
