import socket
import json
timeout = 1 # timeout len used in connection
port = 5025 # port used for connection
buf_sz = 1024 # size of buffer used in recv

class SCPI:
    def __init__(self,addr = "127.0.0.1",commands_file='scpi/commands.json'):
        '''
            params:
                * addr: address of server to connect to
                * commands_file: path to SCPI commands file
            return:
                None
        '''
        '''
        self.addr = addr
        self.soc = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.soc.settimeout(timeout) # time out in secs
        self.soc.connect((addr,port))
        '''
        with open(commands_file,'r') as f:
            commands = json.load(f)
        self.commands = commands
        return
    # ================= common commands functions ================
    def lock_screen(self):
        '''
            params:
                None
            return:
                * servers response to scpi command
        '''
        # lock screen
        self.soc.send(lock_screen)
        ret = self.soc.recv(buf_sz)
        return ret
    # =================
    # ================= other commands functions ================
