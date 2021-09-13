import unittest, numpy as np
from pycta2045.cta2045.handler import CTA2045 as CTA

def print_status(status):
    if status:
        print('SUCESS')
    else:
        print('FAILED')
# device info response's hash is not captured in response['args]. Debug WHY that is.
class TestCTA(unittest.TestCase):
    def test_checksum(self):
        print(f'{"-" * 5} checksum test {"-" * 5}')
        c = CTA()
        shed = "0x08 0x01 0x00 0x02 0x01 0x00 0x0C 0x3D"
        res = c.to_cta("shed")
        print('testing shed....',end='')
        success=True
        for i,j in zip(res.split(' '),shed.split(' ')):
            i = int(i,16)
            j = int(j,16)
            if not j==i:
                success=False
            self.assertEqual(i,j)
        if not res.upper()==shed.upper():
            success=False
        self.assertEqual(res.upper(),shed.upper())
        print_status(success)

        commodity_request = "0x08 0x02 0x00 0x02 0x06 0x00 0xF6 0x4C"
        res = c.to_cta("commodity read request")
        print('testing commodit read request....',end='')
        success=True
        for i,j in zip(res.split(' '),commodity_request.split(' ')):
            i = int(i,16)
            j = int(j,16)
            if not j==i:
                success=False
            self.assertEqual(i,j)
        if not res.upper()==commodity_request.upper():
            success=False
        print_status(success)
        self.assertEqual(res.upper(),commodity_request.upper())

        device_info = "0x08 0x02 0x00 0x02 0x01 0x01 0x04 0x43"
        res = c.to_cta("device info request")
        print('testing device info request....',end='')
        success=True
        for i,j in zip(res.split(' '),device_info.split(' ')):
            i = int(i,16)
            j = int(j,16)
            if not j==i:
                success=False
            self.assertEqual(i,j)
        if not res.upper()==device_info.upper():
            success=False
        print_status(success)
        self.assertEqual(res.upper(),device_info.upper())
        return
    def test_to_cta(self):
        print(f'{"-" * 5} to_cta test {"-" * 5}')
        cta = CTA()
        cmds = cta.cmds['commands']
        for k,v in cmds.items():
            success=True
            v = v['format']
            print(f'testing {k}....',end='')
            res = cta.to_cta(k)
            # check length -- should be greater because of the checksum bytes, which not included in the format
            if not len(res) >= len(v):
                success=False
            self.assertTrue(len(res) >= len(v))
            # assert it doesn't have any alpha values
            for byte in res.split(' '):
                if byte.isalpha():
                    success=False
                self.assertFalse(byte.isalpha())
            print_status(success)
    def test_from_cta(self):
        print(f'{"-" * 5} from_cta test {"-" * 5}')
        cta = CTA()
        cmds = cta.cmds['commands']
        for k,v in cmds.items():
            success=True
            # get hex representation
            print(f"testing {k}...",end='')
            c = cta.to_cta(k)
            # go back to natural language
            res = cta.from_cta(c)
            cmd = res['command']
            # validate key and response
            if not cmd==k:
                success=False
            print_status(success)
            self.assertTrue(k==cmd)
    def test_repeated_args(self):
        print(f'{"-" * 5} repeated arguments test {"-" * 5}')
        cta = CTA()
        # using commodity read response since it is currently the only supported command that uses repeated arguments
        CC0 = cta.get_code_value('commodity_code','electricity consumed')
        CC1 = cta.get_code_value('commodity_code','present energy')
        CA0,CA1 = np.random.randint(0,1000,size=2)
        IR0,IR1 = np.random.randint(0,1000,size=2)
        passed_args = {
            'commodity_code0':CC0,
            'cumulative_amount0':cta.hexify(CA0,length=6),
            'instantaneous_rate0':cta.hexify(IR0,length=6),
            'cumulative_amount1':cta.hexify(CA1,length=6),
            'instantaneous_rate1':cta.hexify(IR1,length=6),
            'commodity_code1':CC1,
        }
        commodity_read_hex = cta.to_cta('commodity read response',args=passed_args.copy())
        # convert back and verify
        returned = cta.from_cta(commodity_read_hex)
        returned_args = returned['args']
        for k,v in passed_args.items(): 
            print('testing',k,'....',end='')
            if k in returned_args:
                returned_value = returned_args[k]
                if 'commodity_code' in k:
                    returned_value = cta.unhexify(cta.get_code_value('commodity_code',returned_value))
                stat = int(returned_value) == int(cta.unhexify(v,combine=True))
                print_status(stat)
        # print(passed_args,returned_args)
if __name__=="__main__":
    unittest.main()
