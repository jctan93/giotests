#!/usr/bin/python
"""debugfs interface for mei driver"""

import codecs
import os
import re
from mei import MEI_MAX_OPEN_HANDLE_COUNT

def open_file_read(path, encoding='UTF-8'):
    '''Open specified file read-only'''
    try:
        orig = codecs.open(path, 'r', encoding)
    except Exception:
        raise

    return orig

def valid_path(path):
    '''Valid path'''
    # No relative paths
    m = "Invalid path: %s" % (path)
    if not path.startswith('/'):
        print "%s (relative)" % (m)
        return False

    if '"' in path:  # We double quote elsewhere
        print "%s (contains quote)" % (m)
        return False

    try:
        os.path.normpath(path)
    except Exception:
        print "%s (could not normalize)" % (m)
        return False

    return os.path.exists(path)

def check_for_debugfs(device):
    """Finds and returns the mointpoint for mei None otherwise"""

    filesystem = '/proc/filesystems'
    mounts = '/proc/mounts'
    support_debugfs = False
    regex_debugfs = re.compile('^\S+\s+(\S+)\s+debugfs\s')
    mei_dir = None

    if valid_path(filesystem):
        with open_file_read(filesystem) as f_in:
            for line in f_in:
                if 'debugfs' in line:
                    support_debugfs = True

    if not support_debugfs:
        return False

    if valid_path(mounts):
        with open_file_read(mounts) as f_in:
            for line in f_in:
                match = regex_debugfs.search(line)
                if match:
                    mountpoint = match.groups()[0] + '/' +  os.path.basename(device)
                    if not valid_path(mountpoint):
                        return False
                    mei_dir = mountpoint

    # Check if meclients are present
    if not valid_path(mei_dir + '/meclients'):
        mei_dir = None
    return mei_dir

def meclients(device):

    meclients = []
    mei_dir = check_for_debugfs(device)
    if not mei_dir:
        return None

    with open_file_read(mei_dir + '/meclients') as f_in:
        header = f_in.readline().strip('\n').split('|')   # skip the first line
        header[0] = 'count'
        for line in f_in:
            s = {}
            values = line.strip('\n').split('|')
            for i in range(len(header)):
                h = header[i].strip(' ')
                s[h] = values[i].strip(' ')
            meclients.append(s)

    return meclients

def client_by_uuid(device, uuid):

    return [i for i in meclients(device) if i['UUID'] == uuid]

def meclients_dyn(device):

    return [i for i in meclients(device) if i['fix'] == "0"]

def num_of_free_cl_conn(device, cl):

    ac = active_conn(device)
    count = int(cl['con']) if cl['fix'] == "0" else 1
    # Skylake: SB buggy clients advertising 255 connections
    count = count if count != 255 else 1
    for i in ac:
        if i['me'] == cl['id'] and int(i['state']) in range(1, 6):
            count -= 1
    return count

def cl_active_conn(device, me):
    ac = active_conn(device)
    return [i for i in active_conn(device) if i['me'] == me]

def active_conn(device):

    active = []
    mei_dir = check_for_debugfs(device)
    if not mei_dir:
        return None

    with open_file_read(mei_dir + '/active') as f_in:
        header = f_in.readline().strip('\n').split('|')   # skip the first line
        header[0] = 'count'
        for line in f_in:
            s = {}
            values = line.strip('\n').split('|')
            for i in range(len(header)):
                h = header[i].strip(' ')
                s[h] = values[i].strip(' ')
            active.append(s)

    return active

def device_free_conn(device):
    """Return number of available connections to device"""
    return MEI_MAX_OPEN_HANDLE_COUNT - len(active_conn(device))

def fixed_address(device, allow):

    mei_dir = check_for_debugfs(device)
    if not mei_dir:
        return

    with open(mei_dir + '/allow_fixed_address', 'r+') as f:
        if allow:
            f.write('Y')
        else:
            f.write('N')

def fixed_address_soft(device, allow):
    '''(Dis)allow fixed address client on old HW only'''

    if get_fa_support(device):
        return

    fixed_address(device, allow)

def num_of_connections(device, uuid):

    for i in meclients(device):
        if i['UUID'] == uuid:
            return int(i['con'])

    return 0

def get_devstate(device):
    """Parse mei devstate"""

    devstate = {}
    hbm = {}
    mei_dir = check_for_debugfs(device)
    if not mei_dir:
        raise Exception("Can't connect to debugfs")

    with open_file_read(mei_dir + '/devstate') as f_in:
        base = 0
        for line in f_in:
            values = line.strip('\n').split(':')
            if base == 0:
                if values[0] == "hbm features":
                    base = 1
                    continue
                devstate[values[0]] = values[1].strip()
            elif base == 1:
                if values[0] == "pg":
                    devstate["pg_enabled"] = values[1].split(',')[0].strip()
                    devstate["pg_state"] = values[1].split(',')[1].strip()
                    continue
                hbm[values[0].strip()] = values[1].strip()
    return devstate, hbm

def get_pg_state(device):
    devstate, hbm = get_devstate(device)
    return devstate["pg"].split(',')[1].strip()

def get_pg_enabled(device):
    devstate, hbm = get_devstate(device)
    return devstate["pg"].split(',')[0].strip()

def get_fa_support(device):
    devstate, hbm = get_devstate(device)
    return int(hbm.get('FA','0'))

def get_ev_support(device):
    devstate, hbm = get_devstate(device)
    return int(hbm.get('EV','0'))
