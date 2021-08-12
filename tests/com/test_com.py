import unittest
import pycta2045.com.handler as COM
import serial.tools.list_ports as lp
from pycta2045.cta2045.handler import CTA2045
import traceback as tb # del

cta = CTA2045()
# these tests depend on an existing serial port 
# please specify an existing serial port to run the tests
port = 'ttyS7' 
class TestCOM(unittest.TestCase):
    def testPortExistFail(self):
        port = 'fake'
        msg = ''
        c = None
        try:
            c = COM.COM(port=port,checksum=cta.checksum,transform=cta.hexify,is_valid=cta.is_valid)
        except Exception as e:
            msg = e.args[0]
        self.assertTrue('not found' in msg)
        self.assertEqual(c,None)
    def testPortExistSuccess(self):
        comports = list(lp.comports())
        print(f'using port: {port}')
        msg = ''
        c = None
        try:
            c = COM.COM(port=f'/dev/{port}',checksum=cta.checksum,transform=cta.hexify,is_valid=cta.is_valid)
        except Exception as e:
            msg = e.args[0]
        self.assertTrue(c != None)
        self.assertTrue(msg == '')

if __name__=="__main__":
    unittest.main()