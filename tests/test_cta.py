import unittest
from agents.cta2045.handler import command_handler as CTA

class TestCTA(unittest.TestCase):
    def test_checksum(self):
        c = CTA()
        shed = "0x08 0x01 0x00 0x02 0x01 0x00 0x0C 0x3D"
        res = c.to_cta("shed")
        for i,j in zip(res.split(' '),shed.split(' ')):
            i = int(i,16)
            j = int(j,16)
            self.assertEqual(i,j)
        self.assertEqual(res.upper(),shed.upper())

if __name__=="__main__":
    unittest.main()
