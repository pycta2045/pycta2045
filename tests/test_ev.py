import unittest
import pandas as pd
from agents.models.ev_model import EV

class TestEV(unittest.TestCase):
    # @unittest.expectedFailure
    def testInit(self):
        c = EV()
        self.assertFalse(c == None)
    def testCharge(self):
        c = EV(max_comfort=1.)
        df = c.charge()
        self.assertFalse(df.shape[0] == 0)
        self.assertTrue(df['soc'].tail(1).values == 1.)
        sz = df.shape[0]
        df = c.charge()
        self.assertFalse(sz == df.shape[0])
    def testGetSoc(self):
        max_comfort = .92
        c = EV(max_comfort=max_comfort)
        df_start = c.charge()
        # get soc at the start -- should be 0
        soc = c.get_soc(time=0)
        self.assertTrue(soc == 0)
        soc = c.get_soc(time=c.t_start)
        self.assertTrue(soc == 0) # should still be zero

        # test at the end -- should be 92%
        soc = c.get_soc(time=c.t_end)
        self.assertTrue(soc == max_comfort) # should still be max comfort

        soc = c.get_soc(time=c.t_end+(60*60)) # get soc 1 hr after end time
        self.assertTrue(soc == max_comfort) # should still be max comfort

        # change max comfort & charge
        max_comfort = 1. # 100%
        c.max_comfort = max_comfort
        df_end = c.charge()
        soc = c.get_soc(time=c.t_end)
        self.assertTrue(soc == max_comfort) # should still be max comfort
        self.assertFalse(df_start.shape[0] >= df_end.shape[0])

    def testGenerateTimestamps(self):
        c = EV()
        df_start = c.charge()

        ts = c.generate_time_stamps()

        # assert the start
        self.assertTrue(ts[0].timestamp() == int(c.t_start))

        j = int(c.t_start)
        for i in ts:
            self.assertTrue(i.timestamp() == j)
            j += c.t_ratio

        # assert the end is within 300 seconds margin -- 5 mins
        self.assertTrue(abs(c.t_end-ts[-1].timestamp())<=300)
        # print(c.max_time/(60*60))#)-ts[-1].timestamp())
        # self.assertTrue(abs(c.max_time-ts[-1].timestamp())<=300)





if __name__=="__main__":
    unittest.main()
