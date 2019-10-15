#!/usr/bin/env python
import argparse
import multiprocessing
import os
import subprocess
from typing import List
from datetime import datetime

from roster_utils import get_device_list, DeviceInfo, show_status


def copy_calibrations_device(device: DeviceInfo):

    filename = "/data/config/calibrations/camera_intrinsic/%s.yaml" % device.hostname

    ssh_host = '%s@%s.local' % (device.username, device.hostname)
    cmd = 'ssh %s "if [ -f %s ]; then \
                      exit 0; \
                   else \
                      exit 3; \
                   fi"' % (ssh_host, filename)
    
    try:
        subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        if e.returncode == 3:
            return "No file"
        return "SSH Error"

    OUTPUT_DIR = '../'
    if "autobot" in device.hostname:
        OUTPUT_DIR = os.path.join(OUTPUT_DIR,'/home/demetris/autolab/ETHZ-AMOD-fleet-roster/autobots')
    else:
        OUTPUT_DIR = os.path.join(OUTPUT_DIR,'/home/demetris/autolab/ETHZ-AMOD-fleet-roster/watchtowers')
    
    date = datetime.today().strftime('%Y-%m-%d')

    if "autobot" in device.hostname:
        OUTPUT_DIR = os.path.join(OUTPUT_DIR,device.hostname,'camera-verification', str("%s-12-00_camera-verification" % date),'calibrations','kinematics')
    else:
        OUTPUT_DIR = os.path.join(OUTPUT_DIR,device.hostname,'intrinsic-calibration', str("%s-12-00_intrinsic-calibration" % date))

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    fn = os.path.join(OUTPUT_DIR, "%s.yaml" % device.hostname)
    
    cmd = 'ssh %s "md5sum %s"' % (ssh_host, filename)
    
    try:
        md5_before_copy = subprocess.check_output(cmd, shell=True)
        md5_before_copy = (md5_before_copy.rstrip().decode("utf-8")).split()[0]
    except subprocess.CalledProcessError:
        return "MD5 error - agent"
    
    cmd = 'sudo scp %s:%s %s' % (ssh_host, filename, fn)
    
    try:
        res = subprocess.check_output(cmd, shell=True)
        res = res.rstrip().decode("utf-8")
    except subprocess.CalledProcessError:
        return "Copy failed"
    
    cmd = 'md5sum %s' % fn
    
    try:
        md5_after_copy = subprocess.check_output(cmd, shell=True)
        md5_after_copy = md5_after_copy.rstrip().decode("utf-8").split()[0]
    except subprocess.CalledProcessError:
        return "MD5 error - server"
    
    if md5_after_copy == md5_before_copy:
        return "MD5 matches"
    else:
        os.unlink(fn)
        return "MD5 mismatch"


def copy_calibrations_all_devices(device_list: List[DeviceInfo]):
    pool = multiprocessing.Pool(processes=20)
    results = pool.map(copy_calibrations_device, device_list)
    pool.close()
    pool.join()

    show_status(device_list, results)

def copy_calibrations_main():

    device_list = get_device_list('/home/demetris/autolab/ETHZ-AMOD-fleet-roster/scripts/device_list.txt')

    print('Copying calibrations:')
    copy_calibrations_all_devices(device_list)


if __name__ == '__main__':
    copy_calibrations_main()