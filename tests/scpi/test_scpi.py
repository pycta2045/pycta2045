import unittest
import pycta2045.scpi.handler as scpi
import multiprocessing
import socket
import time

timeout = 1 # timeout len used in connection
port = 5025 # port used for connection
buf_sz = 1024 # size of buffer used in recv
addr = "127.0.0.1" # using local mock
def MockServer(soc):
    '''
        This is a blocking function that listens to requests from SCPI client
    '''
    cmd = ''
    res = '200'
    try:
        while True:
            (cs,add) = soc.accept()
            data = ''
            try:
                while data != 'QUIT':
                    data = cs.recv(buf_sz)
                    cs.send(res.encode())
                    data = data.decode()
                    print(data)
            except Exception as e:
                print(e)
            cs.close()
        soc.close()
    except Exception as e:
        # server.shutdown(socket.SHUT_RD)
        soc.close()
        print(e)
    return

class TestSCPI(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.server = socket.socket(socket.AF_INET,socket.SOCK_STREAM) # server socket
        self.server.settimeout(timeout) # time out in secs
        self.server.bind((addr,port)) # bind instead of connect
        self.server.listen(5)
        
        self.process = multiprocessing.Process(target=MockServer,args=(self.server,))
        self.process.start()
        # time.sleep(0.02)
        return
    @classmethod
    def tearDownClass(self):
        self.process.terminate()
        self.server.close()
        return

    def testInitFailed(self):
        addr = '0.0.0.1'
        msg = None
        handler = None
        try:
            handler = scpi.SCPI(addr=addr,port=port)
        except Exception as e:
            msg = e.args[0]
        self.assertTrue(handler == None)
        self.assertTrue(msg != None)
        self.assertTrue('failed' in msg)
        return

    def testInitSuccess(self):
        msg = handler = None
        try:
            # open socket on 127.0.0.1
            handler = scpi.SCPI(addr=addr,port=port)
            print('sending QUIT')
            handler.send('QUIT')
        except Exception as e:
            msg = e.args[0]
        self.assertTrue(handler != None)
        self.assertTrue(msg == None)
        return

if __name__=="__main__":
    unittest.main()