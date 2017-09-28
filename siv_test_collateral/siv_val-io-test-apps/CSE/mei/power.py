#!/usr/bin/python
"""power settings for mei driver"""

import codecs

SYSFS_POWER_FMT = '/sys/class/mei/%s/device/power/%s'

def open_file_read(path, encoding='UTF-8'):
    '''Open specified file read-only'''
    try:
        orig = codecs.open(path, 'r', encoding)
    except Exception:
        raise

    return orig

def control_read(dev):
    '''Read from sysfs power control file'''

    with open_file_read(SYSFS_POWER_FMT % (dev, 'control')) as f_in:
        return f_in.readline().strip('\n')

def control_write(dev, value):
    '''Write to sysfs power control file'''

    with open(SYSFS_POWER_FMT % (dev, 'control'), 'w') as f_out:
        f_out.write('%s' % value)

def runtime_pm_is_enabled(dev):
    '''Return True of runtime pm is enabled (set to auto)'''
    return True if control_read(dev) == 'auto' else False

def runtime_pm_enable(dev):
    '''Enable runtime power management (set to auto)'''
    control_write(dev, 'auto')

def runtime_pm_disable(dev):
    '''Disable runtime power management (set to on)'''
    control_write(dev, 'on')

# vim:set sw=4 ts=4 et:
# -*- coding: utf-8 -*-
