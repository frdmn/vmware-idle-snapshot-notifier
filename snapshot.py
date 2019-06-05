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

# Konfigurationsdatei laden
configurationFile = './config.json'
if os.path.isfile(configurationFile):
    with open(configurationFile, 'r') as f:
        config = json.load(f)
else:
    print("Couldn't read config file \"config.json\"")
    sys.exit(1)

def debug_print(msg):
    if config['debug']:
        print(msg)

# Funktion um auf allgemeine VMware API Objekte zuzugreifen
def get_obj(content, vimtype, name):
    obj = None
    container = content.viewManager.CreateContainerView(
        content.rootFolder, vimtype, True)
    for c in container.view:
        if c.name == name:
            obj = c
            break
    return obj

# (Recursive) Funktion um alle aktuellen Snapshots aufzulisten
def list_snapshots_recursively(snapshots):
    snapshot_data = []
    snap_text = ""
    for snapshot in snapshots:
        snap_text = "Name: %s; Description: %s; CreateTime: %s; State: %s" % (snapshot.name, snapshot.description,snapshot.createTime, snapshot.state)
        snapshot_data.append(snap_text)
        snapshot_data = snapshot_data + list_snapshots_recursively(snapshot.childSnapshotList)
    return snapshot_data

# Main Funktion
def main():
    # Versuche Verbindung zur API aufzubauen...
    debug_print("Verindungaufbau zu Server \"%s\" mit Benutzer \"%s\"" % (config['hostname'], config['username']))
    si = connect.Connect(config['hostname'], 443, config['username'], config['password'], sslContext=ssl._create_unverified_context())
    atexit.register(Disconnect, si)
    content = si.RetrieveContent()

    # Erstelle rekursiven ContainerView aus der Wurzel-Ebene der alle VMs enthält
    container = content.rootFolder
    viewType = [vim.VirtualMachine]
    recursive = True
    containerView = content.viewManager.CreateContainerView(container, viewType, recursive)

    children = containerView.view
    # Über VMs iterieren um nach Snapshots zu suchen
    for child in children:
        vm_name = child.summary.config.name

        # Lade VM-Objekt
        vm = get_obj(content, [vim.VirtualMachine], vm_name)

        # Wenn keine Snapshots, for-loop brechen
        if vm.snapshot is None:
            debug_print("VM \"%s\" besitzt aktuell keine Snapshots" % vm.name)
            continue

        # Maschine hat snapshots => alle anzeigen
        snapshot_paths = list_snapshots_recursively(vm.snapshot.rootSnapshotList)
        debug_print("VM \"%s\" besitzt aktuell %d Snapshot:" % (vm.name, len(snapshot_paths)))
        for snapshot in snapshot_paths:
            print(snapshot)

# Start program
if __name__ == "__main__":
    main()
