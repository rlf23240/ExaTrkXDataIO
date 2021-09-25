#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Dict

import pandas as pd


class Event:
    def __init__(
        self,
        event_id: int,
        data: Dict[str, pd.DataFrame]
    ):
        self.event_id = event_id
        self.data = data

    def __getattr__(self, item):
        return self.data[item]

    def __repr__(self):
        str_repr = f"\n======Event {self.event_id}======\n"
        for name, data in self.data.items():
            str_repr += (
                f"- {name}: \n{data.head()}\n...\n"
            )
        str_repr += "==================\n"
        return str_repr

