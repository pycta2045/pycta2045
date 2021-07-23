import unittest
import agents.com.handler as COM
import serial.tools.list_ports as lp


class TestCOM(unittest.TestCase):
    def testPortExistFail(self):
        port = 'fake'
        msg = ''
        c = None
        try:
            c = COM.COM(port=port)
        except Exception as e:
            msg = e.args[0]
        self.assertTrue('not found' in msg)
        self.assertEqual(c,None)
    def testPortExistSuccess(self):
        port = list(lp.comports())[0]
        port=port.name
        msg = ''
        c = None
        try:
            c = COM.COM(port=port)
        except Exception as e:
            msg = e.args[0]
        self.assertTrue(c != None)
        self.assertTrue(msg == '')
if __name__=="__main__":
    unittest.main()
