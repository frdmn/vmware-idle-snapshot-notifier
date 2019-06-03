#!/usr/bin/env python

import atexit
import argparse
import sys
import time
import ssl

from pyVmomi import vim, vmodl
from pyVim.task import WaitForTask
from pyVim import connect
from pyVim.connect import Disconnect, SmartConnect, GetSi

host = 'vcenter.company.de'
user = 'user@vcenter.local'
passw = 'pass'
operation = 'list_all'
vm_name = 'blog.customer.de'

def get_obj(content, vimtype, name):
    obj = None
    container = content.viewManager.CreateContainerView(
        content.rootFolder, vimtype, True)
    for c in container.view:
        if c.name == name:
            obj = c
            break
    return obj

def list_snapshots_recursively(snapshots):
    snapshot_data = []
    snap_text = ""
    for snapshot in snapshots:
        snap_text = "Name: %s; Description: %s; CreateTime: %s; State: %s" % (snapshot.name, snapshot.description, snapshot.createTime, snapshot.state)
        snapshot_data.append(snap_text)
        snapshot_data = snapshot_data + list_snapshots_recursively(snapshot.childSnapshotList)
    return snapshot_data

def main():
    print("Trying to connect to VCENTER SERVER . . .")

    si = connect.Connect(host, 443, user, passw, sslContext=ssl._create_unverified_context())

    # Disconnect upon sigterm
    atexit.register(Disconnect, si)

    print("Connected to VCENTER SERVER !")

    content = si.RetrieveContent()

    vm = get_obj(content, [vim.VirtualMachine], vm_name)

    if not vm:
        print("Virtual Machine %s doesn't exists" % vm_name)
        sys.exit()

    if vm.snapshot is None:
        print("Virtual Machine %s doesn't have any snapshots" % vm.name)
        sys.exit()

    print("Display list of snapshots on virtual machine %s" % vm.name)
    snapshot_paths = list_snapshots_recursively(vm.snapshot.rootSnapshotList)
    for snapshot in snapshot_paths:
        print(snapshot)

    else:
        print("No operation specified")

# Main thread
if __name__ == "__main__":
    main()
