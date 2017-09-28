#!/usr/bin/env python
"""Run get version test against MKHI client with couple of options:
   - read call blocking/non-blocking
   - optionally select before read
   - option to work with fixed client
   - run number of requests in parallel
   - optionally call read before write
"""
import os, time
import threading
import argparse
import select
import mei
import mei.mkhi

def unblocked_getver(fd):
    while 1:
        try:
            mei.mkhi.get_ver(fd)
        except OSError:
            time.sleep(0.1)
            continue
        global gotit
        gotit += 1
        break

def select_getver(fd):
    while 1:
        try:
            select.select([fd], [], [])
            mei.mkhi.get_ver(fd)
        except OSError:
            time.sleep(0.1)
            continue
        global gotit
        gotit += 1
        break

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-b',
        dest='blocking', action='store_true', help='blocking calls')
    parser.add_argument('-s',
        dest='select', action='store_true', help='select calls')
    parser.add_argument('-f',
        dest='fixed', action='store_true', help='connect to fixed mkhi client')
    parser.add_argument('-n',
        dest='threads', type=int, help='number of threads', default=2)
    parser.add_argument('-e',
        dest='early', action='store_true', help='run req before read')
    args = parser.parse_args()

    fd = mei.open_dev_default()

    mei.blocking(fd, args.blocking)
    global gotit
    gotit = 0
    if args.fixed:
        maxlen, vers = mei.mkhi.connect_fixed(fd)
    else:
        maxlen, vers = mei.mkhi.connect(fd)
    if args.early:
        for i in range(0, args.threads):
            mei.mkhi.req_ver(fd)
    for i in range(0, args.threads):
        if args.select:
            worker = threading.Thread(target=select_getver, args=(fd,))
        else:
            worker = threading.Thread(target=unblocked_getver, args=(fd,))
        worker.start()

    time.sleep(1)
    if not args.early:
        for i in range(0, args.threads):
            mei.mkhi.req_ver(fd)
    while 1:
        if gotit == args.threads:
            break
        time.sleep(0.1)
    os.close(fd)
