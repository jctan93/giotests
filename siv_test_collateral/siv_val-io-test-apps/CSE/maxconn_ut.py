#!/usr/bin/env python
"""Test:
      Check number of open handle restrictions
   Procedure:
      1. Open handles to fill all free handles - should succeed
      2. Connect to AMTHIF client (in one of tests)
      3. Open additional handle -  should fail
"""
import os, errno
import unittest
import mei
import mei.amthif
from mei.debugfs import device_free_conn

class MaxOpenTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """fill defaults"""
        cls.devnode = mei.dev_default()

    def setUp(self):
        self.all_fd = []

    def tearDown(self):
        for fd in self.all_fd:
            os.close(fd)

    def test_open_all_plus_fail(self):
        """open maximum available handles plus one"""
        for _ in range(0, device_free_conn(self.devnode)):
            fd = mei.open_dev(self.devnode)
            self.all_fd.append(fd)

        with self.assertRaises(OSError) as cm:
            fd = mei.open_dev(self.devnode)
            self.all_fd.append(fd)

        the_exception = cm.exception
        self.assertEqual(the_exception.errno, errno.EMFILE)

class MaxOpenAmthiTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """fill defaults"""
        cls.devnode = mei.dev_default()
        if not mei.debugfs.client_by_uuid(cls.devnode, mei.amthif.UUID):
            raise unittest.SkipTest("No AMTHIF client")

    def setUp(self):
        self.all_fd = []

    def tearDown(self):
        for fd in self.all_fd:
            os.close(fd)

    def test_open_all_plus_fail(self):
        """open maximum available handles plus one with connect to AMTHIF client"""
        for _ in range(0, device_free_conn(self.devnode)):
            fd = mei.open_dev(self.devnode)
            self.all_fd.append(fd)
            mei.connect(fd, mei.amthif.UUID)

        with self.assertRaises(OSError) as cm:
            fd = mei.open_dev(self.devnode)
            self.all_fd.append(fd)
            mei.connect(fd, mei.amthif.UUID)

        the_exception = cm.exception
        self.assertEqual(the_exception.errno, errno.EMFILE)

if __name__ == '__main__':
    unittest.main()

