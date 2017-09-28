#!/usr/bin/python

"""mkhi helper functions for mei driver"""
import os, struct
import mei

UUID = '8e6a6715-9abc-4043-88ef-9e39c6f63e0f'
FIXED_UUID = '55213584-9a29-4916-badf-0fb7ed682aeb'

def req_ver(fd):

    buf_write = struct.pack("I", 0x000002FF)
    return os.write(fd, buf_write)

def ver_parse(buf_read):

    s = struct.unpack("4B12H", buf_read)
    return s

def get_ver_raw(fd):

    buf_read = os.read(fd, 28)
    return buf_read

def get_ver_raw_by_byte(fd):
    '''Get version byte-by-byte'''
    buf_read = b''
    for _ in range(28):
        buf_read += os.read(fd, 1)
    return buf_read

def get_ver_str(fd):

    buf = get_ver_raw(fd)
    return ver_parse(buf)

def get_ver(fd):

    s = get_ver_str(fd)
    print "ME Code Firmware Version: %d.%d.%d.%d" % (s[5], s[4], s[7], s[6])
    print "ME NFTP Firmware Version: %d.%d.%d.%d" % (s[9], s[8], s[11], s[10])
    print "ME FITC Firmware Version: %d.%d.%d.%d" % (s[13], s[12], s[15], s[14])

def connect(fd):
    return mei.connect(fd, UUID)

def connect_fixed(fd):
    return mei.connect(fd, FIXED_UUID)

def ver(fd):
    req_ver(fd)
    get_ver(fd)
