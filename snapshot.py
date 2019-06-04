#!/usr/bin/env python

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

# (recursive) Funktion um alle aktuellen Snapshots aufzulisten
def list_snapshots_recursively(snapshots):
    snapshot_data = []
    snap_text = ""
    for snapshot in snapshots:
        snap_text = "Name: %s; Description: %s; CreateTime: %s; State: %s" % (snapshot.name, snapshot.description, snapshot.createTime, snapshot.state)
        snapshot_data.append(snap_text)
        snapshot_data = snapshot_data + list_snapshots_recursively(snapshot.childSnapshotList)
    return snapshot_data

# Main Funktion
def main():
    # Versuche Verbindung zur API aufzubauen...
    si = connect.Connect(config['hostname'], 443, config['username'], config['password'], sslContext=ssl._create_unverified_context())
    atexit.register(Disconnect, si)
    content = si.RetrieveContent()

    # Zugriff auf VM-Objekt der eigentlichen virtuellen Maschine
    vm = get_obj(content, [vim.VirtualMachine], config['vm'])

    # Testen ob VM existiert
    if not vm:
        print("Virtual Machine %s doesn't exists" % config['vm'])
        sys.exit(1)

    # Abruch, wenn kein Snapshot vorhanden
    if vm.snapshot is None:
        print("Virtual Machine %s doesn't have any snapshots" % vm.name)
        sys.exit(0)

    # Snapshots ueber list_snapshots_recursively() auflisten
    print("Display list of snapshots on virtual machine %s" % vm.name)
    snapshot_paths = list_snapshots_recursively(vm.snapshot.rootSnapshotList)
    for snapshot in snapshot_paths:
        print(snapshot)
    else:
        print("No operation specified")

    # Script ohne returncode beenden
    sys.exit(0)

# Main thread
if __name__ == "__main__":
    main()
