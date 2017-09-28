#!/usr/bin/env python
"""Test:
      Stress clients
   Procedure:
      1. Open default device
      2. Connect to the client
      3. Send data
      4. Close the connection
"""
import os
import unittest
import fuzzer
import mei
import mei.mkhi
import mei.pavp

class MaxlenStressTestCase(unittest.TestCase):
    uuid = ''
    niter = 1
    def runTest(self):
        '''send random length data byte to client'''
        for _ in range(self.niter):
            fd = mei.open_dev_default()
            maxlen, ver = mei.connect(fd, self.uuid)
            fuzzer.write_random_len(fd, maxlen)
            mei.fsync_or_sleep(fd)
            os.close(fd)

class OneByteStressTestCase(unittest.TestCase):
    uuid = ''
    niter = 1
    def runTest(self):
        '''send 1 byte data to client'''
        for _ in range(self.niter):
            fd = mei.open_dev_default()
            maxlen, ver = mei.connect(fd, self.uuid)
            fuzzer.write_random_len(fd, 1)
            mei.fsync_or_sleep(fd)
            os.close(fd)

def generate_ts(name, base, niter):
    '''generate test suite'''

    uuids = {'mkhi': mei.mkhi.UUID, 'pavp': mei.pavp.UUID}
    stress_ts = unittest.TestSuite()

    for cl_name, uuid in uuids.items():
        test = type("%s:%s:%d" % (name, cl_name, niter), (base,),
                    {'uuid' : uuid, 'niter' : niter})()
        stress_ts.addTest(test)

    return stress_ts

def load_tests(loader, tests, pattern):
    '''prepare test suite for discovery'''
    ts_max_len = generate_ts("MaxlenStressTestCase", MaxlenStressTestCase, 10)
    ts_one_byte = generate_ts("OneByteStressTestCase", OneByteStressTestCase, 100)
    return unittest.TestSuite([ts_max_len, ts_one_byte])

if __name__ == '__main__':
    unittest.main()

# vim:set sw=4 ts=4 et:
# -*- coding: utf-8 -*-

