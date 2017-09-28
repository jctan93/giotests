#!/usr/bin/env python
"""Test:
      Check basic read/write
   Procedure:
      1. Read/write with illegal sizes
      2. Sync functions what should return immediately if no data exists
      3. Read/write, sync functions on non-connected file descriptor
"""
import unittest
import os
import errno
import select
import mei
import mei.mkhi
import mei.debugfs

class ReadWriteBaseTestCase(unittest.TestCase):
    """Basic write/read test"""
    @classmethod
    def setUpClass(cls):
        """fill defaults"""
        cls.devnode = mei.dev_default()

    def setUp(self):
        self.fd = mei.open_dev(self.devnode)
        self.maxlen, _ = mei.mkhi.connect(self.fd)

    def tearDown(self):
        os.close(self.fd)

    def test_zero_write(self):
        '''Test write with 0 data'''
        self.assertEqual(os.write(self.fd, b''), 0)

    def test_zero_read(self):
        '''Test read with 0 data'''
        self.assertEqual(len(os.read(self.fd, 0)), 0)

    def test_big_write(self):
        '''Test write with data of 2*MTU size'''
        data = b'A' * self.maxlen * 2
        with self.assertRaises(OSError) as the_ex:
            os.write(self.fd, data)
        self.assertEqual(the_ex.exception.errno, errno.EFBIG)

    def test_fsync(self):
        '''Test fsync'''
        try:
            os.fsync(self.fd)
        except OSError as err:
            if err.errno != errno.EINVAL:
                raise

    def test_notif_ioctl(self):
        '''Test notification enablement IOCTL'''
        if mei.debugfs.get_ev_support(self.devnode) == 0:
            self.skipTest("Events not supported")
        mei.notif_set(self.fd, 1)
        mei.notif_set(self.fd, 0)

    def test_notif_ioctl_notsupp(self):
        '''Test notification enablement IOCTL on older HW'''
        if mei.debugfs.get_ev_support(self.devnode) != 0:
            self.skipTest("Events supported")
        with self.assertRaises(IOError) as the_ex:
            mei.notif_set(self.fd, 1)
        self.assertEqual(the_ex.exception.errno, errno.EOPNOTSUPP)
        with self.assertRaises(IOError) as the_ex:
            mei.notif_set(self.fd, 0)
        self.assertEqual(the_ex.exception.errno, errno.EOPNOTSUPP)
        with self.assertRaises(IOError) as the_ex:
            mei.notif_get(self.fd)
        self.assertEqual(the_ex.exception.errno, errno.EOPNOTSUPP)

class ReadWriteNotConnectedTestCase(unittest.TestCase):
    """Basic negative write/read and sync tests for not-connected handle"""
    @classmethod
    def setUpClass(cls):
        """fill defaults"""
        cls.devnode = mei.dev_default()

    def setUp(self):
        self.fd = mei.open_dev(self.devnode)

    def tearDown(self):
        os.close(self.fd)

    def test_write(self):
        '''Test write'''
        with self.assertRaises(OSError) as the_ex:
            os.write(self.fd, b'')
        self.assertEqual(the_ex.exception.errno, errno.ENODEV)

    def test_read(self):
        '''Test read'''
        with self.assertRaises(OSError) as the_ex:
            os.read(self.fd, 100)
        self.assertEqual(the_ex.exception.errno, errno.ENODEV)

    def test_fsync(self):
        '''Test fsync'''
        with self.assertRaises(OSError) as the_ex:
            os.fsync(self.fd)
        self.assertIn(the_ex.exception.errno, [errno.ENODEV, errno.EINVAL])

    def test_select(self):
        '''Test select'''
        rlist = [self.fd]
        wlist = xlist = []
        new_rlist, new_wlist, new_xlist = select.select(rlist, wlist, xlist)
        self.assertEqual(rlist, new_rlist)
        self.assertEqual(wlist, new_wlist)
        self.assertEqual(xlist, new_xlist)

    def test_poll(self):
        '''Test poll'''
        poller = select.poll()
        poller.register(self.fd, select.POLLIN | select.POLLERR)
        events = poller.poll()
        poller.unregister(self.fd)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0][1], select.POLLERR)

    def test_notif_ioctl(self):
        '''Test notification enablement IOCTL'''
        if mei.debugfs.get_ev_support(self.devnode) == 0:
            self.skipTest("Events not supported")
        with self.assertRaises(IOError) as the_ex:
            mei.notif_set(self.fd, 1)
        self.assertEqual(the_ex.exception.errno, errno.ENODEV)
        with self.assertRaises(IOError) as the_ex:
            mei.notif_set(self.fd, 0)
        self.assertEqual(the_ex.exception.errno, errno.ENODEV)
        with self.assertRaises(IOError) as the_ex:
            mei.notif_get(self.fd)
        self.assertEqual(the_ex.exception.errno, errno.ENODEV)

    def test_notif_ioctl_notsupp(self):
        '''Test notification enablement IOCTL on older HW'''
        if mei.debugfs.get_ev_support(self.devnode) != 0:
            self.skipTest("Events supported")
        with self.assertRaises(IOError) as the_ex:
            mei.notif_set(self.fd, 1)
        self.assertEqual(the_ex.exception.errno, errno.EOPNOTSUPP)
        with self.assertRaises(IOError) as the_ex:
            mei.notif_set(self.fd, 0)
        self.assertEqual(the_ex.exception.errno, errno.EOPNOTSUPP)
        with self.assertRaises(IOError) as the_ex:
            mei.notif_get(self.fd)
        self.assertEqual(the_ex.exception.errno, errno.EOPNOTSUPP)

if __name__ == '__main__':
    unittest.main()
