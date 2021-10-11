#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ExaTrkXDataIO import DataReader

# Create reader.
reader = DataReader(
    'configs/reader/default.yaml'
)

# Read all event at once.
events = reader.read_all()
print(events)

# Or read one by one if data is too large.
# for event in reader.read():
#    print(event)

# Or read specific event
# event = reader.read_one(evtid=3)
# print(event)
