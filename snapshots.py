#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Dependency imports
import atexit
import argparse
import sys
import time
import ssl
import os
import json
import pytz
import apprise

from datetime import datetime
from pyVmomi import vim, vmodl
from pyVim.task import WaitForTask
from pyVim import connect
from pyVim.connect import Disconnect, SmartConnect, GetSi

# Function to conditionally print debug message
def debug_print(msg):
    if args.debug:
        print(msg)

# Function to calculate days between two dates
def days_between(d1, d2):
    return abs((d2 - d1).days)

# Function to access API objects in general
def get_obj(content, vimtype, name):
    obj = None
    container = content.viewManager.CreateContainerView(
        content.rootFolder, vimtype, True)
    for c in container.view:
        if c.name == name:
            obj = c
            break
    return obj

# (Recursive) function to list all snapshots
def list_snapshots_recursively(vm_name, snapshots):
    snapshot_data = []
    snap_text = ""
    for snapshot in snapshots:
        # Check if min_age_in_days is reached...
        if days_between(snapshot.createTime, today) >= args.min_age_in_days:
            # Check if "NO-REPORT" tag exists...
            if config['no-report-tag'] in snapshot.description:
                print("No-Report-Tag found in snapshot description of \"%s\". Skip reporting..." % (vm_name))
                break

            # Otherwise add snapshot to results dict
            snap_text = "VM: %s; SnapshotName: %s; Description: %s; CreatedAt: %s; AgeInDays: %s; Status: %s" % (vm_name, snapshot.name, snapshot.description, snapshot.createTime, days_between(snapshot.createTime, today), snapshot.state)
            snapshot_data.append(snap_text)
            snapshot_data = snapshot_data + list_snapshots_recursively(vm_name, snapshot.childSnapshotList)
    return snapshot_data

# Function to send out apprise notification
def send_notification(subject, message):
    appriseInstance.notify(title=subject, body=message)
    return

# Main function
def main():
    # Try to establish connection to API
    debug_print("Trying to establish connection to server \"%s\" using account \"%s\"..." % (config['hostname'], config['username']))
    si = connect.Connect(config['hostname'], 443, config['username'], config['password'], sslContext=ssl._create_unverified_context())
    atexit.register(Disconnect, si)
    content = si.RetrieveContent()

    debug_print("Looking for snapshots older than %d days..." % args.min_age_in_days)

    # Create recursive container view from root level that contains all existing VMs
    container = content.rootFolder
    viewType = [vim.VirtualMachine]
    recursive = True
    containerView = content.viewManager.CreateContainerView(container, viewType, recursive)

    children = containerView.view
    # Iterate over VMs to look for snapshots
    for child in children:
        vm_name = child.summary.config.name

        # Create VM object for current (index) VM
        vm = get_obj(content, [vim.VirtualMachine], vm_name)

        # Continue for loop in case there are no snapshots
        if vm.snapshot is None:
            debug_print("\"%s\": no snapshots available" % vm.name)
            continue

        # List snapshots
        snapshot_paths = list_snapshots_recursively(vm_name, vm.snapshot.rootSnapshotList)
        for snapshot in snapshot_paths:
            print("\"%s\": found affected snapshot - %s" % (vm.name, snapshot))
            send_notification(vm.name, snapshot)

# Create argument parser
parser = argparse.ArgumentParser(description='Report idle VMware snapshots')
parser.add_argument('--min-age-in-days', type=int, help='The minimum age in days of snapshots to report')
parser.add_argument('--config', help='Path to configuration file')
parser.add_argument('--debug', action='store_true', help='Enable debug mode (optional)')
args = parser.parse_args()

# Check for required arguments
if not args.min_age_in_days:
    print('Error: missing --min-age-in-days argument!')
    sys.exit(1)

# Load config file
configurationFile = './config.json'

if args.config:
    if os.path.isfile(args.config):
        configurationFile = args.config
    else:
        print("Couldn't read config file \"%s\"" % args.config)
        sys.exit(1)

if os.path.isfile(configurationFile):
    with open(configurationFile, 'r') as f:
        config = json.load(f)
else:
    print("Couldn't read config file \"%s\"" % configurationFile)
    sys.exit(1)

config['no-report-tag'] = "[NO-REPORT]"

# Store todays date
today = datetime.utcnow().replace(tzinfo=pytz.UTC)

# Initiate apprise instance to send out notifications
appriseInstance = apprise.Apprise()
appriseInstance.add(config['notification'])

# Initiate main function
if __name__ == "__main__":
    main()
