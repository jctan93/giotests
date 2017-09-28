#!/usr/bin/env python
"""Test:
      stress_byte.py [<UUID>] - send single byte to a firmware client in loop
   Procedure:
      1. Check connetion to supplied or first firemware client
      2. stress tests in loop (2000)
         2.1 open
         2.2 connect
         2.3. write a byte
         2.4. close
"""

import os
import sys
import errno
import mei
from mei.debugfs import meclients_dyn

def stress_write(fd, uuid_str, data):
    "Send data rapidly to ME clients"
    for i in range(0, 2000):
        fd = mei.open_dev_default()
        maxlen, vers = mei.connect(fd, uuid_str)
        print "%d: writing %d bytes to %s" % (i, len(data), uuid_str)
        os.write(fd, data)
        mei.fsync_or_sleep(fd)
        os.close(fd)

def main():
    uuid_str = None
    try:
        uuid_str = sys.argv[1]
    except IndexError:
        devnode = mei.dev_default()
        uuid_str = meclients_dyn(devnode)[0]['UUID']

    fd = mei.open_dev_default()
    try:
        mei.connect(fd, uuid_str)
    except IOError as err:
        if err.errno == errno.ENOTTY:
            print "Error: Cannot find %s client" % uuid_str
            exit(1)
        else:
            raise

    os.close(fd)

    stress_write(fd, uuid_str, b'A')

if __name__ == '__main__':
    main()

