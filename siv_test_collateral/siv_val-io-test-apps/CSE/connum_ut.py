#!/usr/bin/env python
"""Test:
      Connect to different clients
"""
import os, errno
import unittest
import mei
from mei.debugfs import meclients_dyn, meclients, num_of_free_cl_conn

class ConnectOneTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """fill defaults"""
        cls.devname = mei.dev_default_name()
        cls.devnode = mei.to_dev(cls.devname)
        mei.debugfs.fixed_address_soft(cls.devname, True)

    @classmethod
    def tearDownClass(cls):
        """Cleanup state"""
        mei.debugfs.fixed_address_soft(cls.devname, False)

    def setUp(self):

        self.all_fd = []

    def tearDown(self):
        """free all open handles"""
        for fd in self.all_fd:
            os.close(fd)

    def find_cl_by_numconn(self, numconn):
        """find client with at least numconn free connections"""
        clients = meclients_dyn(self.devnode)
        return next(cl for cl in clients if num_of_free_cl_conn(self.devnode, cl) >= numconn)

    def find_cl_by_numconn_exact(self, numconn):
        """find client with numconn free connections"""
        clients = meclients_dyn(self.devnode)
        return next(cl for cl in clients if num_of_free_cl_conn(self.devnode, cl) == numconn)

    def find_cl_fixed_with_free(self):
        """find fixed client with free connection"""
        clients = meclients(self.devnode)
        return next(cl for cl in clients if cl['fix'] != "0" and num_of_free_cl_conn(self.devnode, cl) > 0)

    def test_twoconn_dyn_success(self):
        """connect twice in parallel to client with at least two connections"""
        cl = self.find_cl_by_numconn(2)
        fd1 = mei.open_dev(self.devnode)
        self.all_fd.append(fd1)
        fd2 = mei.open_dev(self.devnode)
        self.all_fd.append(fd2)
        mei.connect(fd1, cl['UUID'])
        mei.connect(fd2, cl['UUID'])

    def test_twoconn_dyn_fail(self):
        """connect twice in parallel to client with only one connection"""
        cl = self.find_cl_by_numconn_exact(1)
        fd1 = mei.open_dev(self.devnode)
        self.all_fd.append(fd1)
        fd2 = mei.open_dev(self.devnode)
        self.all_fd.append(fd2)
        mei.connect(fd1, cl['UUID'])
        with self.assertRaises(IOError) as cm:
            mei.connect(fd2, cl['UUID'])

        the_exception = cm.exception
        self.assertEqual(the_exception.errno, errno.EBUSY)

    def test_oneconn_fix_success(self):
        """connect once to fixed client"""
        cl = self.find_cl_fixed_with_free()
        fd1 = mei.open_dev(self.devnode)
        self.all_fd.append(fd1)
        mei.connect(fd1, cl['UUID'])

    def test_twoconn_fix_fail(self):
        """connect twice in parallel to fixed client"""
        cl = self.find_cl_fixed_with_free()
        fd1 = mei.open_dev(self.devnode)
        self.all_fd.append(fd1)
        fd2 = mei.open_dev(self.devnode)
        self.all_fd.append(fd2)
        mei.connect(fd1, cl['UUID'])
        with self.assertRaises(IOError) as cm:
            mei.connect(fd2, cl['UUID'])

        the_exception = cm.exception
        self.assertEqual(the_exception.errno, errno.EBUSY)

class ConnectAllTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """fill defaults"""
        cls.devname = mei.dev_default_name()
        cls.devnode = mei.to_dev(cls.devname)
        mei.debugfs.fixed_address_soft(cls.devname, True)

    @classmethod
    def tearDownClass(cls):
        """Cleanup state"""
        mei.debugfs.fixed_address_soft(cls.devname, False)

    def setUp(self):

        self.all_fd = []

    def tearDown(self):
        """free all open handles"""
        for fd in self.all_fd:
            os.close(fd)

    def test_conn_once_success(self):
        """connect once to every client"""
        for cl in meclients(self.devnode):
            if num_of_free_cl_conn(self.devnode, cl) < 1:
                continue
            fd = mei.open_dev(self.devnode)
            self.all_fd.append(fd)
            mei.connect(fd, cl['UUID'])

    def test_conn_all_success(self):
        """connect to all available connections of all clients"""
        for cl in meclients(self.devnode):
            for _ in range(0, num_of_free_cl_conn(self.devnode, cl)):
                fd = mei.open_dev(self.devnode)
                self.all_fd.append(fd)
                mei.connect(fd, cl['UUID'])

if __name__ == '__main__':
    unittest.main()

