import socket
import time
import pandas as pd
import json
import os


timeout = 1 # timeout len used in connection
port = 5025 # port used for connection
buf_sz = 1024 # size of buffer used in recv

class SCPI:
    def __init__(self,addr = "192.168.0.153",commands_file='commands.json',log_file='log',logging=False):
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
        try:
            self.soc = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.soc.settimeout(timeout) # time out in secs
            self.soc.connect((addr,port))
            print("connected!")
            with open(f'{path}/{commands_file}','r') as f:
                commands = json.load(f)
            self.commands = commands
            self.type = {0: 'command',1: 'query',2: 'configure'}
            self.log_file = log_file+'.csv'
            self.logging=logging
        except Exception as e:
            # close socket
            # if self.SOC 
            self.soc.close()
            raise Exception(f"failed to open socket on {addr}:{port}")

        return
    def log(self,l):
        l['time'] = int(time.time()) 
        #print(l)
        df = pd.DataFrame(l)
        df.set_index('time',inplace=True)
        df.to_csv(self.log_file,mode='a',header=False)
        return

    def send_command(self,cmd,recv=False):
        '''
            * Purpose: sends a command through the socket
            * Args:
                * cmd: desired command
            * Return:
                * returns received value from simulator if recv is true (expect a value in return)
                * returns status (True/False) of sent message
        '''
        r = self.soc.send(f"{cmd}\n".encode())
        if recv:
            ret = self.soc.recv(buf_sz).decode()
            ret = ret.split('\n')[0]
        else:
            ret = True
        return ret

    def send(self,cmd,cmd_type=0,args=None):
        '''
            * Purpose: wrapper for send_command
            * Args:
                * cmd: desired command
                * cmd_type: [ 0: command | 1: query | 2: configure]
                        - commands returns None
                        * queries return values (str) 
                        - configure returns None
                * args: argument for command/query
            * Return:
                * returns received value from simulator if cmd_type is query
                * returns status (True/False) value from simulator if cmd_type is command/configure
        '''
        status = False
        try:
            t = self.type[cmd_type]
            # find command in commands dict
            cmd = self.commands[t][cmd]
            # consider args for command
            if not args is None:
                cmd = f"{cmd} {' '.join(args)}"
            # check if we expect to receive something back ( check if cmd_type is query )
            recv = t == 'query'
            # send command
            res = self.send_command(cmd,recv) # send command 
            status = True

        except Exception as e:
            res = e
        if self.logging:
            self.log({'command':[cmd],'response':[res],'status':[status]})
        return (status,res)

print(__name__)
