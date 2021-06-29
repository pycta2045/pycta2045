import unittest
import agents.scpi.handler as scpi
import socket

addr = ''
port = 9000
class TestSCPI(unittest.TestCase):
    def setUp(self):
        serversocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        serversocket.connect(('',port))
    def tearDown(self):
        serversocket.close()
    def testInitFailed(self):
        addr = '0.0.0.0'
        msg = None
        handler = None
        try:
            handler = scpi.SCPI(addr=addr)
        except Exception as e:
            msg = e.args[0]
        self.assertTrue(handler == None)
        self.assertTrue(msg != None)
        self.assertTrue('failed' in msg)

    def testInitSuccess(self):
        msg = ss = handler = None
        try:
            # open socket on 127.0.0.1
            ss = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            ss.connect((addr,port))
            handler = scpi.SCPI(addr=addr)
            print("HERE SUCCESS")
        except Exception as e:
            msg = e.args[0]
            ss.close()
        self.assertTrue(handler != None)
        self.assertTrue(msg == None)

if __name__=="__main__":
    unittest.main()
