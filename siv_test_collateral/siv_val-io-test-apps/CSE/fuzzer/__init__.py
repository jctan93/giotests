#!/usr/bin/env python
"""fuzzer module
"""
import random
import os
import struct

def write_random_len(fd, buf_len):
    '''
    write random filled buffer of set length
    '''
    random.seed()
    data = b''
    for i in range(buf_len):
        data += struct.pack('>b', random.randint(0, 127))
    os.write(fd, data)

def write_random_uptolen(fd, max_len):
    '''
    write random filled buffer of random length between [0, max_len]
    '''
    random.seed()
    write_random_len(fd, random.randint(0, max_len))

def write_random_len_iter(fd, buf_len, n):
    '''
    write random data buffer of length buf_len n times
    '''
    for i in range(n):
        write_random_len(fd, buf_len)

def write_random_uptolen_iter(fd, max_len, n):
    '''
    write random filled buffer of random length between [0, max_len] n times
    '''
    for i in range(n):
        write_random_uptolen(fd, max_len)

# vim:set sw=4 ts=4 et:
# -*- coding: utf-8 -*-
