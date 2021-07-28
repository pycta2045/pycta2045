import unittest
import agents.com.handler as COM
import serial.tools.list_ports as lp
from agents.cta2045.handler import CTA2045

cta = CTA2045()
class TestCOM(unittest.TestCase):
    def testPortExistFail(self):
        port = 'fake'
        msg = ''
        c = None
        try:
            c = COM.COM(port=port,checksum=cta.checksum,transform=cta.hexify)
        except Exception as e:
            msg = e.args[0]
        self.assertTrue('not found' in msg)
        self.assertEqual(c,None)
    def testPortExistSuccess(self):
        comports = list(lp.comports())
        if len(comports)>0:
            port = comports[0]
            port=port.name
            print(f'using port: {port}')
            msg = ''
            c = None
            try:
                c = COM.COM(port=port,checksum=cta.checksum,transform=cta.hexify)
            except Exception as e:
                msg = e.args[0]
            self.assertTrue(c != None)
            self.assertTrue(msg == '')
if __name__=="__main__":
    unittest.main()
