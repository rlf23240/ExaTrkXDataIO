#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ExaTrkXDataIO import DataReader

reader = DataReader(
    'configs/reader/default.yaml'
)
events = reader.read_all()
print(events)
