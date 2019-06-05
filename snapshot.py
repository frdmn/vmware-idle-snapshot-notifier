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

from pyVmomi import vim, vmodl
from pyVim.task import WaitForTask
from pyVim import connect
from pyVim.connect import Disconnect, SmartConnect, GetSi

# Load config file
configurationFile = './config.json'
if os.path.isfile(configurationFile):
    with open(configurationFile, 'r') as f:
        config = json.load(f)
else:
    print("Couldn't read config file \"config.json\"")
    sys.exit(1)

# Function to conditionally print debug message
def debug_print(msg):
    if config['debug']:
        print(msg)

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
        snap_text = "VM: %s; SnapshotName: %s; Description: %s; CreatedAt: %s; Status: %s" % (vm_name, snapshot.name, snapshot.description,snapshot.createTime, snapshot.state)
        snapshot_data.append(snap_text)
        snapshot_data = snapshot_data + list_snapshots_recursively(vm_name, snapshot.childSnapshotList)
    return snapshot_data

# Main function
def main():
    # Try to establish connection to API
    debug_print("Trying to establish connection to server \"%s\" using account \"%s\"" % (config['hostname'], config['username']))
    si = connect.Connect(config['hostname'], 443, config['username'], config['password'], sslContext=ssl._create_unverified_context())
    atexit.register(Disconnect, si)
    content = si.RetrieveContent()

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
            debug_print("VM \"%s\" doesn't have any" % vm.name)
            continue

        # List snapshots
        snapshot_paths = list_snapshots_recursively(vm_name, vm.snapshot.rootSnapshotList)
        debug_print("VM \"%s\" has %d snapshots:" % (vm.name, len(snapshot_paths)))
        for snapshot in snapshot_paths:
            print(snapshot)

# Start program
if __name__ == "__main__":
    main()
