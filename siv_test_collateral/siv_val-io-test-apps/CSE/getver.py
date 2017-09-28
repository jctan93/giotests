#!/usr/bin/env python
"""Test:
      Get firmware version via MKHI
   Procedure:
      1. Open default device
      2. Connect to the MKHI client
      3. Request version (send/receive)
      4. Close the connection
"""
import os
import mei, mei.mkhi

if __name__ == '__main__':

    fd = mei.open_dev_default()

    try:
        mei.mkhi.connect(fd)
    except IOError as e:
        if e.errno == 25:
            print "Errro: Cannot find MKHI Client"
            exit(1)
        else:
            raise

    mei.mkhi.ver(fd)
    os.close(fd)

