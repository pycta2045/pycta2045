import unittest

class TestCharger(unittest.TestCase):
    @unittest.expectedFailure
    def test_fun1(self):
        self.assertEqual("hi",'hello')

if __name__=="__main__":
    unittest.main()
