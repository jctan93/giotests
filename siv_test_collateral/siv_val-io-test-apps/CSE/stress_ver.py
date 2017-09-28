#!/usr/bin/env python
"""Test:
      Send data rapidly get version. 2000 iterations
   Procedure:
   1. Open default device
   2. Check the connection
   3. In Loop
     3.1 Open default device
     3.2 Connect to the MKHI client
     3.3 Request version (send/receive)
     3.4 Close the connection
"""
import os
import mei
import mei.mkhi

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
    os.close(fd)

    for n in range(0, 2000):
        fd = mei.open_dev_default()
        maxlen, vers = mei.mkhi.connect(fd)
        mei.mkhi.ver(fd)
        os.close(fd)
