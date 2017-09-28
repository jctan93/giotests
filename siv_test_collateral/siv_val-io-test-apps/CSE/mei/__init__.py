#!/usr/bin/env python
"""mei module
"""
import array, fcntl, os, uuid, struct, sys
import time
import errno

MEI_MAX_OPEN_HANDLE_COUNT = 255

def_dev_names = ["mei0", "mei"]
def to_dev(name):
    """return device path by device name"""
    return "/dev/%s" % name

def dev_default_name():
    """return default mei device name"""
    for dev_name in def_dev_names:
        if os.access(to_dev(dev_name), os.F_OK):
            return dev_name

    raise IOError(errno.ENODEV, "No device found", "/dev/mei*");

def dev_default():
    """return default mei device string"""
    for devnode in [to_dev(s) for s in def_dev_names]:
        if os.access(devnode, os.F_OK):
            return devnode

    raise IOError(errno.ENODEV, "No device found", "/dev/mei*");

def open_dev(devnode):
    return os.open(devnode, os.O_RDWR)

def open_dev_default():
    devnode = dev_default()
    return os.open(devnode, os.O_RDWR)

def blocking(fd, block):
    nf = fcntl.fcntl(fd, fcntl.F_GETFL)

    if block:
        nf = nf & ~os.O_NONBLOCK
    else:
        nf = nf | os.O_NONBLOCK

    fcntl.fcntl(fd, fcntl.F_SETFL, nf)

def connect(fd, uuid_str):

    IOCTL_MEI_CONNECT_CLIENT = 0xc0104801
    cl_uuid = uuid.UUID(uuid_str)
    buf = array.array('b', cl_uuid.bytes_le)
    fcntl.ioctl(fd, IOCTL_MEI_CONNECT_CLIENT, buf, 1)
    maxlen, vers = struct.unpack("<IB", buf.tostring()[:5])
    # print "connected %s, maxlen %x, vers %x" % (uuid_str, maxlen, vers)

    return maxlen, vers

def notif_set(fd, request):
    '''Call notification set IOCTL'''
    IOCTL_MEI_NOTIFY_SET = 0x40044802
    buf = struct.pack("I", request)
    fcntl.ioctl(fd, IOCTL_MEI_NOTIFY_SET, buf)

def notif_get(fd):
    '''Call notification get IOCTL'''
    IOCTL_MEI_NOTIFY_GET = 0x80044803
    buf = ''
    fcntl.ioctl(fd, IOCTL_MEI_NOTIFY_GET, buf)
    return struct.unpack("I", buf)

def fsync_or_sleep(fd):
    '''run fsync if available, or sleep 0.1sec'''
    try:
        os.fsync(fd)
    except OSError as err:
        if err.errno == errno.EINVAL:
            time.sleep(0.1)
        else:
            raise
