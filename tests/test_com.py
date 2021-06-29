import unittest
import agents.com.handler as COM


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
        port = 'tty0'
        msg = ''
        c = None
        try:
            c = COM.COM(port=port)
        except Exception as e:
            msg = e.args[0]
        self.assertFalse(c != None)
        self.assertFalse(msg == '')
if __name__=="__main__":
    unittest.main()
