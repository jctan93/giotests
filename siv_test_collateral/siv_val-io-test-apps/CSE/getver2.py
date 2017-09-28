#!/usr/bin/env python
"""Test:
   1. Open default device twice
   2. Connect to the all dynamic MKHI instances
   3. Request get version from the each connection
   4. Close the connections
"""
import mei, os
import mei.mkhi
import mei.debugfs

if __name__ == '__main__':

    fd = []
    devnode = mei.dev_default()
    con = mei.debugfs.num_of_connections(devnode, mei.mkhi.UUID)

    if con == 0:
        print "Error: MKHI not found"
        exit(1)

    for i in range(con):
        fd.append(mei.open_dev_default())

    for i in range(con):
        try:
            mei.mkhi.connect(fd[i])
        except IOError as e:
            if e.errno == 25:
                print "Errro: Cannot find MKHI Client"
                exit(1)
            else:
                raise

    for i in range(con):
        mei.mkhi.ver(fd[i])

    for i in range(con):
        os.close(fd[i])

