#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Any
from pathlib import Path

import numpy as np
import pandas as pd

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


# Define PyGPickleParser only when PyG is proper installed.
try:
    import torch
    import torch_geometric

    class PyGPickleParser(EventFileParser):
        def load(self, path: Path) -> Any:
            return torch.load(path, map_location='cpu')

        def extract(self, data: Any, tag: str) -> np.array:
            return getattr(data, tag).numpy()

except ImportError:
    class PyGPickleParser(EventFileParser):
        def load(self, path: Path) -> Any:
            raise RuntimeError(
                'PyG not found.'
                'Please install PyTorch Geometric to use PyGPickleParser.'
            )

        def extract(self, data: Any, tag: str) -> np.array:
            raise RuntimeError(
                'PyG not found.'
                'Please install PyTorch Geometric to use PyGPickleParser.'
            )

# Define TensorboardLogParser only when tb is proper installed.
try:
    from tensorboard.backend.event_processing import event_accumulator

    class TensorboardLogParser(EventFileParser):
        def load(self, path: Path) -> Any:
            events = event_accumulator.EventAccumulator(str(path))
            events.Reload()

            return events

        def extract(self, data: Any, tag: str) -> np.array:
            return np.array(data.Scalars(tag))

except ImportError:
    class TensorboardLogParser(EventFileParser):
        def load(self, path: Path) -> Any:
            raise RuntimeError(
                'Tensorboard not found.'
                'Please install PyTorch Geometric to use PyGPickleParser.'
            )

        def extract(self, data: Any, tag: str) -> np.array:
            raise RuntimeError(
                'Tensorboard not found.'
                'Please install PyTorch Geometric to use PyGPickleParser.'
            )
