#!/usr/bin/python
'''iAMT watchdog helper'''
import os
import os.path
import errno
import fnmatch
import array
import fcntl

class NoIdentityException(Exception):
    '''Exception raised if no identity file found in sysfs'''
    pass

def wdt_identity_sysfs(identity="iamt_wdt"):
    '''Search for mei watchdog in sysfs'''

    wd_root = "/sys/class/watchdog/"
    for wd_dir in os.listdir(wd_root):
        try:
            with open(os.path.join(wd_root, wd_dir) + "/identity") as wd_f:
                if wd_f.read().split()[0] == identity:
                    return "/dev/" + wd_dir
        except IOError as err:
            if err.errno == errno.ENOENT:
                raise NoIdentityException()
            else:
                raise
    raise IOError(errno.ENOENT, "iAMT watchdog is not found")

def wdt_identity_ioctl(identity="iamt_wdt"):
    '''Search for mei watchdog using IOCTL'''

    busy_wd = False
    WDIOC_GETSUPPORT = 0x80285700
    for wd_dev in os.listdir("/dev/"):
        if not fnmatch.fnmatch(wd_dev, "watchdog*"):
            continue
        try:
            with open(os.path.join("/dev/", wd_dev)) as wd_f:
                buf = array.array('b', '\0' * 40)
                fcntl.ioctl(wd_f, WDIOC_GETSUPPORT, buf, True)
                if buf[8:].tostring().rstrip('\0') == identity:
                    return "/dev/" + wd_dev
        except IOError as err:
            if err.errno == errno.EBUSY:
                busy_wd = True
            else:
                raise
    if busy_wd:
        raise OSError(errno.EBUSY, "Some watchdog is busy")
    else:
        raise IOError(errno.ENOENT, "iAMT watchdog is not found")

def iamt_wdt_get(identity="iamt_wdt"):
    '''Search for mei watchdog'''
    try:
        return wdt_identity_sysfs(identity)
    except NoIdentityException:
        pass

    return wdt_identity_ioctl(identity)

def iamt_wdt_is_available():
    '''Checks iAMT wdt availability'''
    try:
        wdt_fd = os.open(iamt_wdt_get(), os.O_RDWR)
        os.close(wdt_fd)
    except IOError as err:
        if err.errno == errno.ENOENT:
            return False
        raise
    except OSError as err:
        if err.errno == errno.EBUSY:
            return False
        raise
    return True

def iamt_wdt_is_open():
    '''Checks if iAMT wdt is open'''
    try:
        wdt_fd = os.open(iamt_wdt_get(), os.O_RDWR)
        os.close(wdt_fd)
    except IOError as err:
        if err.errno == errno.ENOENT:
            return False
        raise
    except OSError as err:
        if err.errno == errno.EBUSY:
            return True
        raise
    return False
