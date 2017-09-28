#!/usr/bin/env python
"""Test:
      Check that driver is entering, exiting PG
   Procedure:
      1. Check if runtime pm is enabled for device
         and do following steps in right order
      2. Enable/disable runtime pm
      3. Check that driver status shows right PM state
"""
from time import sleep
import unittest
from mei.debugfs import get_devstate
import mei.power

def get_pg_state(devnode):
    return get_devstate(devnode)[0]["pg_state"]

class CheckStateTestCase(unittest.TestCase):
    """Check that driver is entering, exiting PG"""

    @classmethod
    def setUpClass(cls):
        """get devnode and check if PG supported at all"""
        cls.devname = mei.dev_default_name()
        cls.devnode = mei.to_dev(cls.devname)
        if get_devstate(cls.devnode)[0]["pg_enabled"] != "ENABLED":
            raise unittest.SkipTest("PG not supported")

    def test_change_state(self):
        """test change PG state"""
        if not mei.power.runtime_pm_is_enabled(self.devname):
            sleep(1)
            self.assertEqual(get_pg_state(self.devnode), "OFF")
            mei.power.runtime_pm_enable(self.devname)
            sleep(1)
            self.assertEqual(get_pg_state(self.devnode), "ON")
            mei.power.runtime_pm_disable(self.devname)
            sleep(1)
            self.assertEqual(get_pg_state(self.devnode), "OFF")
        else:
            sleep(1)
            self.assertEqual(get_pg_state(self.devnode), "ON")
            mei.power.runtime_pm_disable(self.devname)
            sleep(1)
            self.assertEqual(get_pg_state(self.devnode), "OFF")
            mei.power.runtime_pm_enable(self.devname)
            sleep(1)
            self.assertEqual(get_pg_state(self.devnode), "ON")

if __name__ == '__main__':

    unittest.main()
