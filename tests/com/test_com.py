import unittest
from unittest.mock import MagicMock,patch, create_autospec
import pycta2045.com.handler as COM
import serial.tools.list_ports as lp
from pycta2045.cta2045.handler import CTA2045
import serial,time
from serial import SerialException


cta = CTA2045()
class TestCOM(unittest.TestCase):
    def testPortExistFail(self):
        port = 'fake'
        msg = ''
        c = None
        print('-'*5,'test port exists fails','-'*5)
        try:
            c = COM.COM(port=port,transform=cta.hexify,is_valid=cta.is_valid)
        except SerialException as e:
            msg = e.__str__()
        except Exception as e:
            msg = e.args[0]
        self.assertTrue('could not open' in msg)
        self.assertEqual(c,None)
    
    @patch('serial.Serial')
    def testPortExistSuccess(self,mod):
        port = 'ttyS0'
        msg = ''
        c = None
        print('-'*5,'test port exists succeeds','-'*5)
        try:
            c = COM.COM(port=f'/dev/{port}',transform=cta.hexify,is_valid=cta.is_valid)
        except Exception as e:
            msg = e.args[0]
        self.assertTrue(c != None)
        self.assertTrue(msg == '')
    
    @patch('serial.Serial')
    def testSend(self,mod):
        port = 'ttyS0'
        c = None
        print('-'*5,'test com send','-'*5)
        c = COM.COM(port=f'/dev/{port}',transform=cta.hexify,is_valid=cta.is_valid)
        self.assertTrue(c != None)
        c.ser.write = MagicMock(return_value=2)

        for cmd in ['shed','endshed','loadup','operating status request']:
            sent_cmd = cta.to_cta(cmd)
            sent_cmd_bytes = cta.to_cta_bytes(cmd)
            ret = c.send(sent_cmd)
            c.ser.write.assert_called_with(sent_cmd_bytes)
    
    @patch('serial.Serial')
    def testRecv(self,mod):
        port = 'ttyS0'
        c = None
        print('-'*5,'test receive','-'*5)
        c = COM.COM(port=f'/dev/{port}',transform=cta.hexify,is_valid=cta.is_valid)
        self.assertTrue(c != None)
        c.ser.inWaiting = MagicMock(return_value=0)
        c.start() # start listener
        for cmd in ['shed','endshed','loadup','operating status request']:
            sent_cmd = cta.to_cta(cmd)
            sent_cmd_bytes = cta.to_cta_bytes(cmd)
            c.ser.read = MagicMock(return_value=sent_cmd_bytes)
            c.ser.inWaiting = MagicMock(return_value=len(sent_cmd_bytes))
            time.sleep(1)
            ret = c.get_next_msg()
            if ret != None:
                ret,_ = ret
                self.assertTrue(sent_cmd == ret)
        c.stop()

    @patch('serial.Serial')
    def testDelay(self,mod):
        self.assertTrue(True)

if __name__=="__main__":
    unittest.main()