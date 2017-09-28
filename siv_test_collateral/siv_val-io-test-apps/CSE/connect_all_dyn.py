#!/usr/bin/env python
"""Test:
      connect_all_dyn - connect all dynamic address clients
   Procedure:
      2. stress tests in loop (2000)
         2.1 open
         2.2 connect
         2.3. write a byte
         2.4. close
"""
import os
import mei
import errno
from mei.debugfs import meclients_dyn, cl_active_conn

def main():

    devnode = mei.dev_default()
    clients = meclients_dyn(devnode)
    data = b'A'
    for cl in clients:
        uuid = cl['UUID']
        me = cl['id']
        cnt_con = int(cl['con'])
        fd = mei.open_dev(devnode)
        try:
            maxlen, vers = mei.connect(fd, uuid)
        except IOError as e:
            err, strerror = e.args
            if err == errno.EBUSY and len(cl_active_conn(devnode, me)) == cnt_con:
                print "%s: skipping already connected" % (uuid)
            else:
                print '%s: Error :%s' % (uuid, strerror)
            os.close(fd)
            continue
        print '%s: success' % (uuid)
        os.write(fd, data)
        os.close(fd)

if __name__ == '__main__':
    main()
