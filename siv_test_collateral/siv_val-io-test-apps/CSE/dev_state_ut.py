#!/usr/bin/env python
"""Test:
      Check that driver is alive and ready
   Procedure:
      1. Read debugfs devstate entry
      2. Check that driver is in ready state
"""
import unittest
import mei
from mei.debugfs import get_devstate, meclients

class CheckStateTestCase(unittest.TestCase):

    def setUp(self):
        self.devnode = mei.dev_default()

    def test_state(self):
        dev_state, hbm_features = get_devstate(self.devnode)
        self.assertEqual(dev_state["dev"], "ENABLED")
        self.assertEqual(dev_state["hbm"], "STARTED")

    def test_client_list(self):
        clients = meclients(self.devnode)
        self.assertGreater(len(clients), 0)

if __name__ == '__main__':
    unittest.main()
