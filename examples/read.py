#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ExaTrkXDataIO import DataReader

# Create reader.
reader = DataReader(
    'configs/reader/default.yaml'
)

# Read all event at once.
events = reader.read_all()

# Show result.
print(events)
