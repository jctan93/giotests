#!/usr/bin/python
"""sysfs interface for mei driver"""

def sysfs_path(device, node):
    '''Prepare sysfs path'''
    return "/sys/class/mei/%s/%s" % (device, node)

def hbm_ver(device):
    '''Return HBM version'''
    with open(sysfs_path(device, "hbm_ver")) as hbm_fp:
        ver_str = hbm_fp.read()

    return float(ver_str)

def hbm_ver_drv(device):
    '''Return driver HBM version'''
    with open(sysfs_path(device, "hbm_ver_drv")) as hbm_fp:
        ver_str = hbm_fp.read()

    return float(ver_str)

def fw_status(device):
    '''Return driver FW status'''
    sts = []
    with open(sysfs_path(device, "fw_status")) as sts_fp:
        for line in sts_fp:
            sts.append(int(line, 16))
    return sts
