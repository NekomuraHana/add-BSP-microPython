"""Continuously scan for 1 second and print advertised name/service UUIDs.

Does not connect to devices. Displays UUIDs present in received advertisements,
not the complete remote GATT database. Ctrl-C stops the loop.
"""
from ubluepy import Scanner
from ble_parse_adv import advertising_info

while True:
    for entry in Scanner().scan(1000):
        name, services = advertising_info(entry)
        print("addr:", entry.addr(), "name:", name if name is not None else "(none)",
              "primary services:", services if services else "(not advertised)")
