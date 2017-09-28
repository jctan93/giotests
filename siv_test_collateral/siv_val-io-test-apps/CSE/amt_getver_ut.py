#!/usr/bin/env python
"""Test:
      Get firmware version via AMTHIF
   Procedure:
      1. Open default device
      2. Connect to the AMTHIF client
      3. Request version
      4. Sleep 1 sec (if requested)
      5. Read response
      6. Close the connection
"""
import os
import time
import random
import unittest
import mei.amthif
import mei.debugfs

class GetVersionBaseTestCase(unittest.TestCase):
    """Basic write/read test"""
    @classmethod
    def setUpClass(cls):
        """fill defaults"""
        cls.devnode = mei.dev_default()
        if not mei.debugfs.client_by_uuid(cls.devnode, mei.amthif.UUID):
            raise unittest.SkipTest("No AMTHIF client")

    def setUp(self):
        self.fd = mei.open_dev(self.devnode)
        mei.amthif.connect(self.fd)

    def tearDown(self):
        os.close(self.fd)

    def cmpsize(self, timeout=0):
        '''Send request and read reply for get version'''
        mei.amthif.req_ver(self.fd)
        if timeout:
            time.sleep(timeout)
        buf = mei.amthif.get_ver_silent(self.fd)
        self.assertGreater(len(buf), 2)

    def test_cmpsize(self):
        '''Get version'''
        self.cmpsize()

    def test_cmpsize_sleep(self):
        '''Get version with 1 sec sleep'''
        self.cmpsize(1)

    def test_cmpsize_50(self):
        '''Get version 50 time in loop'''
        for _ in (0, 50):
            self.cmpsize()

    def test_cmpsize_sleep_50(self):
        '''Get version with 1 sec sleep 50 time in loop'''
        for _ in (0, 50):
            self.cmpsize(1)

class GetVersionParallelTestCase(unittest.TestCase):
    """Get version in parallel through number of connections"""
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

    def parallel(self, conn=2, timeout=0):
        '''Request version from two connections in parallel'''
        for _ in range(0, conn):
            fd = mei.open_dev(self.devnode)
            self.all_fd.append(fd)
            mei.amthif.connect(fd)
        for fd in self.all_fd:
            mei.amthif.req_ver(fd)
        if timeout:
            time.sleep(timeout)
        for fd in random.sample(self.all_fd, conn):
            buf = mei.amthif.get_ver_silent(fd)
            self.assertGreater(len(buf), 2)

    def test_parallel(self):
        '''Request version from two connections in parallel'''
        self.parallel()

    def test_parallel_timeout(self):
        '''Request version from two connections in parallel with 1 sec sleep'''
        self.parallel(timeout=1)

class GetVersionWithWriteOnlyTestCase(unittest.TestCase):
    """Get version with more writes then reads"""
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

    def test_2normal_1writeonly(self):
        '''Send three requests, request reply from two of them'''
        for _ in range(0, 3):
            fd = mei.open_dev(self.devnode)
            self.all_fd.append(fd)
            mei.amthif.connect(fd)
        for idx in range(0, 3):
            mei.amthif.req_ver(self.all_fd[idx])

        buf = mei.amthif.get_ver_silent(self.all_fd[0])
        self.assertGreater(len(buf), 2)
        buf = mei.amthif.get_ver_silent(self.all_fd[2])
        self.assertGreater(len(buf), 2)

    def test_1normal_and_writeonly(self):
        '''Send two requests, request reply from one of them'''
        fd = mei.open_dev(self.devnode)
        self.all_fd.append(fd)
        mei.amthif.connect(fd)
        mei.amthif.req_ver(fd)
        mei.amthif.req_ver(fd)

        buf = mei.amthif.get_ver_silent(fd)
        self.assertGreater(len(buf), 2)

if __name__ == '__main__':
    unittest.main()
