import unittest
from agents.cta2045.handler import CTA2045 as CTA

# @TODO:
# device info response's hash is not captured in response['args]. Debug WHY that is.
class TestCTA(unittest.TestCase):
    def test_checksum(self):
        print(f'{"-" * 5} to_cta test {"-" * 5}')
        c = CTA()
        shed = "0x08 0x01 0x00 0x02 0x01 0x00 0x0C 0x3D"
        res = c.to_cta("shed")
        print('testing shed....',end='')
        for i,j in zip(res.split(' '),shed.split(' ')):
            i = int(i,16)
            j = int(j,16)
            self.assertEqual(i,j)
        self.assertEqual(res.upper(),shed.upper())
        print("SUCCESS")

        commodity_request = "0x08 0x02 0x00 0x02 0x06 0x00 0xF6 0x4C"
        res = c.to_cta("commodity read request")
        print('testing commodit read request....',end='')
        for i,j in zip(res.split(' '),commodity_request.split(' ')):
            i = int(i,16)
            j = int(j,16)
            self.assertEqual(i,j)
        self.assertEqual(res.upper(),commodity_request.upper())
        print("SUCCESS")

        device_info = "0x08 0x02 0x00 0x02 0x01 0x01 0x04 0x43"
        res = c.to_cta("device info request")
        print('testing device info request....',end='')
        for i,j in zip(res.split(' '),device_info.split(' ')):
            i = int(i,16)
            j = int(j,16)
            self.assertEqual(i,j)
        self.assertEqual(res.upper(),device_info.upper())
        print("SUCCESS")
    
    def test_to_cta(self):
        print(f'{"-" * 5} to_cta test {"-" * 5}')
        cta = CTA()
        cmds = cta.cmds['commands']
        for k,v in cmds.items():
            print(f'tesing {k}....',end='')

            c = cta.to_cta(k)
            # check length
            self.assertTrue(len(c) >= len(v))
            # assert it doesn't have any alpha values
            for byte in c.split(' '):
                self.assertFalse(byte.isalpha())
            print('SUCESS')
    def test_from_cta(self):
        print(f'{"-" * 5} from_cta test {"-" * 5}')
        cta = CTA()
        cmds = cta.cmds['commands']
        for k,v in cmds.items():
            # get hex representation
            print(f"testing {k}...",end='')
            c = cta.to_cta(k)
            # go back to natural language
            res = cta.from_cta(c)
            print(c)
            cmd = res['command']
            # validate key and response
            self.assertTrue(cmd==k)
            print('SUCESS')
if __name__=="__main__":
    unittest.main()
