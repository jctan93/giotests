#!/usr/bin/env python
"""Test:
      Get firmware version via AMTHIF
   Procedure:
      1. Open default device
      2. Connect to the AMTHIF client
      3. Request version (send/receive)
      4. Close the connection
"""
import os
import errno
import mei, mei.amthif

if __name__ == '__main__':

    fd = mei.open_dev_default()

    try:
        mei.amthif.connect(fd)
    except IOError as err:
        if err.errno == errno.ENOTTY:
            print "Error: Cannot find AMTHIF Client"
            exit(1)
        else:
            raise

    mei.amthif.ver(fd)
    os.close(fd)

