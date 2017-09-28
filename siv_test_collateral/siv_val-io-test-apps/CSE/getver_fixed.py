#!/usr/bin/env python
"""Test:
      get firmware version via fixed address MKHI client
   Procedure:
      1. Open default device
      2. Eneble access to the fixed addresses
      2. Connect to the MKHI Fixed address client
      3. Request version (send/receive)
      4. Close the connection
"""
import os
import mei
import mei.mkhi
from mei.debugfs import fixed_address_soft

def main():
    """Tests:
       1. Open default device
       2. Eneble access to the fixed addresses
       2. Connect to the MKHI Fixed address client
       3. Request version (send/receive)
       4. Close the connection
    """

    devnode = mei.dev_default()
    try:
        fixed_address_soft(devnode, True)
    except Exception as e:
        print "Errro: cannot enable fixed address"
        raise

    fd = mei.open_dev(devnode)

    try:
        mei.mkhi.connect_fixed(fd)
    except IOError as e:
        if e.errno == 25:
            print "Errro: Cannot find MKHI Client"
            exit(1)
        else:
            raise

    mei.mkhi.ver(fd)
    os.close(fd)

    fixed_address_soft(devnode, False)

if __name__ == '__main__':
    main()

