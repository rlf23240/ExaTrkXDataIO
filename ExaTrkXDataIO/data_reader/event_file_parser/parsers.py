#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Any
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from .event_file_parser import EventFileParser


class NumpyNPZParser(EventFileParser):
    def load(self, path: Path) -> Any:
        return np.load(str(path))

    def extract(self, data: Any, tag: str) -> np.array:
        return data[tag]


class PandasCSVParser(EventFileParser):
    def load(self, path: Path) -> pd.DataFrame:
        return pd.read_csv(path)

    def extract(self, data: pd.DataFrame, tag: str) -> np.array:
        return data[tag].to_numpy()


class PyGPickleParser(EventFileParser):
    def load(self, path: Path) -> Any:
        return torch.load(path, map_location='cpu')

    def extract(self, data: Any, tag: str) -> np.array:
        return getattr(data, tag).numpy()
