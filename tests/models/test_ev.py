import unittest
import pandas as pd
from datetime import datetime as dt
from pycta2045.models.ev_model import EV

class TestEV(unittest.TestCase):
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
        soc = soc[-1]
        self.assertTrue(soc == 0)
        soc = c.get_soc(time=c.t_start)
        soc = soc[-1]
        self.assertTrue(soc == 0) # should still be zero

        # test at the end -- should be 92%
        soc = c.get_soc(time=c.t_end)
        # soc = soc[-1]
        self.assertTrue(soc == max_comfort) # should still be max comfort

        soc = c.get_soc(time=c.t_end+(60*60)) # get soc 1 hr after end time
        soc = soc[-1]
        self.assertTrue(soc == max_comfort) # should still be max comfort

        # change max comfort & charge
        max_comfort = 1. # 100%
        c.max_comfort = max_comfort
        df_end = c.charge()
        soc = c.get_soc(time=c.t_end)
        # soc = soc[-1]
        self.assertTrue(soc == max_comfort) # should still be max comfort
        self.assertFalse(df_start.shape[0] >= df_end.shape[0])
    def testGenerateTimestamps(self):
        c = EV()
        df_start = c.charge()

        ts = c.generate_time_stamps()

        # assert the start
        self.assertTrue(ts[0].tz_localize('US/Pacific').timestamp() == int(c.t_start))

        times = pd.date_range(start=dt.fromtimestamp(c.t_start),end=dt.fromtimestamp(c.t_end),periods=len(c.currs)).round('S')
        for i,j in zip(ts,times):
            self.assertTrue(i.timestamp() == j.timestamp())
        # assert the end is within 300 seconds margin -- 5 mins
        self.assertTrue(abs(c.t_end-ts[-1].tz_localize('US/Pacific').timestamp())<=300)
        # self.assertTrue(abs(c.max_time-ts[-1].timestamp())<=300)

if __name__=="__main__":
    unittest.main()