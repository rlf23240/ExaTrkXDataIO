#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod

import numpy as np


class EventDataProcessor(ABC):
    @abstractmethod
    def process(self, data: np.array, **kwargs) -> np.array:
        pass
