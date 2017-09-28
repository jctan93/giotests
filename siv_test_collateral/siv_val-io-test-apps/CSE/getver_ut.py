#!/usr/bin/env python
"""Test:
      Get firmware version via MKHI
   Procedure:
      1. Open default device
      2. Connect to the MKHI client
      3. Request version
      4. Sleep 1 sec (if requested)
      5. Read response and check version length
      6. Close the connection
"""
import os, time
import errno
import unittest
import threading
import select
import mei
import mei.mkhi
from mei.debugfs import fixed_address_soft

class GetVersionBaseTestCase(unittest.TestCase):
    '''Abstract testcase, can be run over different UUID'''
    def setUp(self):
        self.buf = []
        self.gotit = 0
        self.fd = mei.open_dev_default()
        self.lock = threading.Lock()
        try:
            mei.connect(self.fd, self.UUID)
        except IOError as err:
            if err.errno == errno.ENOTTY:
                print "Error: Cannot find MKHI Client"
                exit(1)
            else:
                raise
        mei.mkhi.req_ver(self.fd)
        self.ver_sample = mei.mkhi.get_ver_raw(self.fd)
        if len(self.ver_sample) != 28:
            raise EnvironmentError(errno.EFAULT, "Sample version have a wrong size")

    def tearDown(self):
        os.close(self.fd)

    def getver_thread(self, num):
        '''Get version thread'''
        self.buf[num] = mei.mkhi.get_ver_raw(self.fd)
        with self.lock:
            self.gotit += 1

    def getver_thread_select(self, num):
        '''Get version thread with select'''
        select.select([self.fd], [], [])
        self.buf[num] = mei.mkhi.get_ver_raw(self.fd)
        with self.lock:
            self.gotit += 1

    def getver_thread_loop(self, num):
        '''Get version thread run in loop'''
        while 1:
            try:
                self.buf[num] = mei.mkhi.get_ver_raw(self.fd)
            except OSError as err:
                if err.errno == errno.EAGAIN:
                    time.sleep(0.1)
                    continue
                raise
            with self.lock:
                self.gotit += 1
            break

    def cmp_thread(self, num, after, thread_func):
        '''Get version with rx in num threads'''
        self.buf = [""] * num
        self.gotit = 0
        if not after:
            for _ in range(0, num):
                mei.mkhi.req_ver(self.fd)
        for i in range(0, num):
            worker = threading.Thread(target=thread_func, args=(i,))
            worker.start()
        if after:
            for _ in range(0, num):
                mei.mkhi.req_ver(self.fd)
        while 1:
            if self.gotit == num:
                break
            time.sleep(0.1)
        for i in range(0, num):
            self.assertEqual(self.buf[i], self.ver_sample)

    def cmp(self, timeout_before=0, timeout=0, bytebyte=False):
        '''Send request and read reply for get version'''
        if timeout_before:
            time.sleep(timeout_before)
        mei.mkhi.req_ver(self.fd)
        if timeout:
            time.sleep(timeout)
        if bytebyte:
            buf = mei.mkhi.get_ver_raw_by_byte(self.fd)
        else:
            buf = mei.mkhi.get_ver_raw(self.fd)
        self.assertEqual(buf, self.ver_sample)

    def test_cmp(self):
        '''Get version'''
        self.cmp()

    def test_cmp_by_byte(self):
        '''Get version byte by byte'''
        self.cmp(bytebyte=True)

    def test_cmp_sleep(self):
        '''Get version with 1 sec sleep'''
        self.cmp(timeout=1)

    def test_cmp_sleep_before(self):
        '''Get version with 1 sec sleep before send'''
        self.cmp(timeout_before=1)

    def test_cmp_50(self):
        '''Get version 50 time in loop'''
        for _ in (0, 50):
            self.cmp()

    def test_cmp_sleep_50(self):
        '''Get version with 1 sec sleep 50 time in loop'''
        for _ in (0, 50):
            self.cmp(timeout=1)

    @unittest.skip("Fail without read sync")
    def test_thread_100(self):
        '''Get version with rx in 100 threads'''
        self.cmp_thread(100, after=False, thread_func=self.getver_thread)

    @unittest.skip("Fail without read sync")
    def test_thread_contrariwise_100(self):
        '''Get version with rx in 100 threads with tx after rx'''
        self.cmp_thread(100, after=True, thread_func=self.getver_thread)

    def test_thread_unblocked_100(self):
        '''Get version with rx in 100 threads using non-blocking read'''
        mei.blocking(self.fd, False)
        self.cmp_thread(100, after=False, thread_func=self.getver_thread_loop)
        mei.blocking(self.fd, True)

    def test_thread_unblocked_after_100(self):
        '''Get version with rx in 100 threads using non-blocking read
           with tx after rx'''
        mei.blocking(self.fd, False)
        self.cmp_thread(100, after=True, thread_func=self.getver_thread_loop)
        mei.blocking(self.fd, True)

    @unittest.skip("Fail without read sync")
    def test_thread_select_100(self):
        '''Get version with rx in 100 threads using select'''
        self.cmp_thread(100, after=False, thread_func=self.getver_thread_select)

    @unittest.skip("Fail without read sync")
    def test_thread_select_after_100(self):
        '''Get version with rx in 100 threads using select with tx after rx'''
        self.cmp_thread(100, after=True, thread_func=self.getver_thread_select)

    @unittest.skip("FIXME: Always contaminates other tests")
    def test_forewer_blocked_thread(self):
        '''Get version with rx in thread and no tx,
           leaves thread blocked on read'''
        worker = threading.Thread(target=self.getver_thread, args=(0,))
        worker.start()
        time.sleep(0.5)
        self.assertEqual(self.gotit, 0)

class GetVersionTestCase(GetVersionBaseTestCase):
    '''Test case over dynamic MKHI client'''
    def __init__(self, methodName='runTest'):
        GetVersionBaseTestCase.__init__(self, methodName)
        self.UUID = mei.mkhi.UUID

class GetVersionFixedTestCase(GetVersionBaseTestCase):
    '''Test case over fixed MKHI client'''
    def __init__(self, methodName='runTest'):
        GetVersionBaseTestCase.__init__(self, methodName)
        self.UUID = mei.mkhi.FIXED_UUID

    @classmethod
    def setUpClass(cls):
        cls.devnode = mei.dev_default()
        try:
            fixed_address_soft(cls.devnode, True)
        except Exception:
            print "Error: cannot enable fixed address"
            raise

    @classmethod
    def tearDownClass(cls):
        fixed_address_soft(cls.devnode, False)

def load_tests(loader, tests, pattern):
    '''prepare test suite for discovery'''
    tests1 = loader.loadTestsFromTestCase(GetVersionTestCase)
    tests2 = loader.loadTestsFromTestCase(GetVersionFixedTestCase)
    return unittest.TestSuite([tests1, tests2])

if __name__ == '__main__':
    unittest.main()

