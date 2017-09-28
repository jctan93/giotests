#!/usr/bin/env python
"""Test:
   1. Open default device twice
   2. Connect to N AMTHIF instances
   3. Request get version from the each connection
   4. Close the connections
"""
import mei, os
import argparse
import mei.amthif

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-n', dest='conn', type=int, help='number of connections', default=10)
    args = parser.parse_args()

    fd = []
    dev_node = mei.dev_default()

    for i in range(args.conn):
        fd.append(mei.open_dev(dev_node))

    for i in range(args.conn):
        try:
            mei.amthif.connect(fd[i])
        except IOError as err:
            if err.errno == 25:
                print "Errro: Cannot find AMTHIF Client"
                exit(1)
            else:
                raise

    for i in range(args.conn):
        print "Connection", i + 1
        mei.amthif.ver(fd[i])
        print "---------------"

    for i in range(args.conn):
        os.close(fd[i])

