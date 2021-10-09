#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np

from .event_data_processor import EventDataProcessor


class Transpose(EventDataProcessor):
    def process(self, data: np.array, **kwargs) -> np.array:
        return np.transpose(data, kwargs['axes'])


class Select(EventDataProcessor):
    def process(self, data: np.array, **kwargs) -> np.array:
        if 'column' in kwargs:
            return data[:, kwargs['column']]
        if 'row' in kwargs:
            return data[kwargs['row'], :]
        return data
