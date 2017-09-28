#!/usr/bin/env python
"""Test:
      Check that load/unload works
   Procedure:
      1. Unload/load driver
      2. Read debugfs devstate entry
      3. Check that driver is in ready state
"""
import os
import unittest
import errno
import subprocess
import time
import mei
from mei.debugfs import get_devstate, meclients
from mei.watchdog import iamt_wdt_get, iamt_wdt_is_available, iamt_wdt_is_open

class ReloadTestCase(unittest.TestCase):
    '''Check that load/unload works'''

    def __init__(self, methodName='runTest'):
        self.devnode = ''
        unittest.TestCase.__init__(self, methodName)

    def _test_state(self):
        '''check driver state'''
        dev_state, _ = get_devstate(self.devnode)
        self.assertEqual(dev_state["dev"], "ENABLED")
        self.assertEqual(dev_state["hbm"], "STARTED")

    def _test_client_list(self):
        '''check number of enumerated clients'''
        clients = meclients(self.devnode)
        self.assertGreater(len(clients), 0)

    @staticmethod
    def is_loaded():
        '''return True if mei driver is loaded'''
        with open("/proc/modules") as modules:
            return modules.read().find("mei_me") != -1

    @staticmethod
    def depends():
        '''Find dependencies'''
        with open("/proc/modules", "r") as mod_f:
            for line in mod_f:
                fields = line.split()
                if fields[0] == 'mei':
                    return [x for  x in fields[3].split(',') if x != "mei_me"]
        raise EOFError()

    @staticmethod
    def module_load():
        '''Load mei driver using modprobe'''
        if subprocess.call("modprobe -q mei_me", shell=True) != 0:
            raise OSError(errno.ENODEV, "Failed to load driver")
        #try to load all modules on bus
        subprocess.call("modprobe -q mei_wdt", shell=True)
        subprocess.call("modprobe -q mei_dal", shell=True)
        subprocess.call("modprobe -q mei_spd", shell=True)
        subprocess.call("modprobe -q mei_phy", shell=True)
        time.sleep(0.5)

    @staticmethod
    def module_unload():
        '''Unload mei driver using modprobe'''
        dep = ReloadTestCase.depends()
        if subprocess.call("modprobe -raq %s mei_me" %
                           ' '.join(str(p) for p in dep),
                           shell=True) != 0:
            raise OSError(errno.ENODEV, "Failed to remove driver")
        time.sleep(0.5)

    def loaded(self):
        '''Load module and check it health'''
        if not self.is_loaded():
            self.module_load()
        self.devnode = mei.dev_default()
        self._test_state()
        self._test_client_list()

    def unloaded(self):
        '''Unload module and check that it's down'''
        if self.is_loaded():
            self.module_unload()
        with self.assertRaises(IOError) as the_exp:
            mei.dev_default()
        self.assertEqual(the_exp.exception.errno, errno.ENODEV)

    @unittest.skipIf(iamt_wdt_is_open(), "iAMT watchdog is open")
    def test_loop50(self):
        '''Loop 50 times in unload/load pattern'''
        for _ in range(0, 50):
            self.unloaded()
            self.loaded()

    @unittest.skipIf(iamt_wdt_is_open(), "iAMT watchdog is open")
    def test_reload_once(self):
        '''Do once unload/load pattern'''
        self.unloaded()
        self.loaded()

    @unittest.skipIf(iamt_wdt_is_open(), "iAMT watchdog is open")
    def test_unload_with_open_conn(self):
        '''Test module unload with connection opened'''
        self.loaded()
        fd = mei.open_dev_default()
        with self.assertRaises(OSError) as the_exp:
            self.module_unload()
        self.assertEqual(the_exp.exception.errno,
                         errno.ENODEV)
        os.close(fd)
        self.assertTrue(self.is_loaded())
        self.module_load()

    @unittest.skipUnless(iamt_wdt_is_available(),
                         "iAMT wdt is not found or busy")
    def test_unload_with_open_wdt_conn(self):
        '''Test module unload with wdt connection opened'''
        self.loaded()
        wdt_fd = os.open(iamt_wdt_get(), os.O_RDWR)
        with self.assertRaises(OSError) as the_exp:
            self.module_unload()
        self.assertEqual(the_exp.exception.errno, errno.ENODEV)
        os.close(wdt_fd)
        self.assertTrue(self.is_loaded())

if __name__ == '__main__':
    unittest.main()
