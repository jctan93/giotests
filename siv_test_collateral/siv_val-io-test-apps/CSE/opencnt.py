#!/usr/bin/python
"""Test:
      Check possible number of opened file handles
   Procedure:
      1. Open default device in loop
   Todo:
      Max open change according platform and kernel version
"""
import errno
import mei
import mei.debugfs

MAX_OPEN_FD = 255

def verdict(i, free_conn):
    '''check actual number of opened fd against the constant'''
    if i == free_conn:
        print "OK"
        return 0
    elif i < free_conn:
        print "BAD: possible to open only %d (which is less then %d)" %(i, MAX_OPEN_FD)
        return 1
    elif i > free_conn:
        print "BAD: possible too many %d (which is more then %d)" %(i, MAX_OPEN_FD)
        return 2

def test():
    '''Check possible number of opened file handles'''
    dev_node = mei.dev_default()
    free_conn = mei.debugfs.device_free_conn(dev_node)
    for i in range(0, 2 * MAX_OPEN_FD):
        try:
            mei.open_dev(dev_node)
        except OSError as err:
            # 24 Too many open files
            if err.errno == errno.EMFILE:
                exit(verdict(i, free_conn))
            else:
                raise

if __name__ == '__main__':

    test()
