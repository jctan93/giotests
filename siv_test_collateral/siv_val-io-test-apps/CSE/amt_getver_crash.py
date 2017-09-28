#!/usr/bin/env python
"""Test:
      Get crash while receiving firmware version via AMTHIF
   Procedure:
      1. In thread open default device
      2. Connect to the AMTHIF client
      3. Request version (recv)
      4. Crash in main thread
"""
import os
import errno
import time
import threading
import mei
import mei.amthif

def crash_func():
    '''this will crash after 1sec'''

    fd = mei.open_dev_default()

    try:
        mei.amthif.connect(fd)
    except IOError as err:
        if err.errno == errno.ENOTTY:
            print "Error: Cannot find AMTHIF Client"
            exit(1)
        else:
            raise

    mei.amthif.get_ver(fd)
    os.close(fd)

def work():
    '''Start the worker thread'''

    worker = threading.Thread(target=crash_func)
    worker.daemon = True
    worker.start()


if __name__ == '__main__':

    work()

    time.sleep(1)

    CRASH = 123/0

