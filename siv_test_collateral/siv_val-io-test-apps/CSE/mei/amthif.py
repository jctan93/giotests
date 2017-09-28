#!/usr/bin/python

"""amthif helper functions for mei driver"""
import os, struct
import mei

UUID = '12f80028-b4b7-4b2d-aca8-46e0ff65814c'

def req_ver(fd):

    buf_write = struct.pack("BBHII", 1, 1, 0, 0x0400001A, 0)
    return os.write(fd, buf_write)

def ver_parse(buf_read):

    return struct.unpack("<BBHIII65BI", buf_read)

def get_ver_raw(fd):

    buf_read = os.read(fd, 16 + 65 + 4)
    return buf_read

def get_ver_str(fd):

    buf = get_ver_raw(fd)
    return ver_parse(buf)

def get_sub_ver_raw(fd):

    buf_read = os.read(fd, 44)
    return buf_read

def get_ver_silent(fd):

    ver_str = get_ver_str(fd)
    all_ver = {"BIOS Version": bytearray(ver_str[7:71]).decode("utf-8")}
    for _ in range(0, ver_str[71]):
        sub_ver = struct.unpack("<H20BH20B", get_sub_ver_raw(fd))
        all_ver[bytearray(sub_ver[1:sub_ver[0] + 1]).decode("utf-8")] = \
            bytearray(sub_ver[22:sub_ver[21] + 22]).decode("utf-8")
    return all_ver

def get_ver(fd):

    all_ver = get_ver_silent(fd)
    for ver_name in sorted(all_ver):
        print "%-20s : %s" % (ver_name, all_ver[ver_name])

def connect(fd):
    return mei.connect(fd, UUID)

def ver(fd):
    req_ver(fd)
    get_ver(fd)
