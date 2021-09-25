#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
from importlib import import_module

import pandas as pd
import yaml

from ..event import Event
from .event_file_parser.parsers import (
    NumpyNPZParser,
    PandasCSVParser,
    PyGPickleParser
)
from .event_data_processor.processors import (
    Transpose,
    Select
)


class DataReader:
    _default_parsers = {
        'numpy.npz': NumpyNPZParser,
        'pandas.csv': PandasCSVParser,
        'pyg.pickle': PyGPickleParser
    }

    _default_processors = {
        'transpose': Transpose(),
        'select': Select()
    }

    def __init__(self, config_path, base_dir=None):
        try:
            with open(config_path) as fp:
                self.config = yaml.load(fp, Loader=yaml.SafeLoader)
        except IOError:
            print("Configuration file cannot be open: ", str(config_path))
            exit(1)
        except yaml.YAMLError:
            print("Cannot parse file as YAML format: ", str(config_path))
            exit(1)

        self._set_base_dir(base_dir)
        self._set_event_ids()
        self._set_parsers()
        self._set_processor()
        self._set_event_def()

    def _set_base_dir(self, base_dir):
        # Set base directory.
        if base_dir is None:
            self.base_dir = Path()
        else:
            self.base_dir = Path(base_dir)

    def _set_event_ids(self):
        # Get event IDs.
        if 'evtid' not in self.config:
            raise KeyError(
                'Event ID definition not found.'
                'Make sure you define "evtid" section in correct way.'
            )

        evtid_def = self.config['evtid']
        if 'range' in evtid_def:
            self.event_ids = list(range(
                evtid_def['range'][0],
                evtid_def['range'][1]
            ))
        elif 'indices' in evtid_def:
            self.event_ids = evtid_def['indices']
        else:
            raise TypeError('Event ID not define properly.')

    def _set_parsers(self):
        # Define parsers.
        self.parsers = self._default_parsers
        if 'parsers' in self.config:
            for module_name, class_names in self.config['parsers'].items():
                module = import_module(module_name)
                for name, class_name in class_names.items():
                    self.parsers[name] = getattr(module, class_name)

    def _set_processor(self):
        self.processors = self._default_processors
        if 'processors' in self.config:
            for module_name, class_names in self.config['processors'].items():
                module = import_module(module_name)
                for name, class_name in class_names.items():
                    self.processors[name] = getattr(module, class_name)

    def _set_event_def(self):
        if 'event' not in self.config:
            raise KeyError(
                'Event data definition not found.'
                'Make sure you define "event" section in correct way.'
            )

        self.event_def = self.config['event']

        # Sanity checks.
        """for name, data_def in self.event_def.items():
            if 'parser' not in data_def:
                raise KeyError(
                    'Parser definition not found in data definition "{name}".'
                    'Make sure you define "parser" in correct way.'
                )
            if data_def['parser'] not in self.parsers:
                raise KeyError(
                    f'Parser cannot be find for "{name}".'
                    'Make sure your parser can be found with correct module path.'
                )
            if 'file' not in data_def:
                raise KeyError(
                    'File definition not found in data definition "{name}".'
                    'Make sure you define "file" in correct way.'
                )
            if 'tags' not in data_def:
                raise KeyError(
                    'Tags definition not found in data definition "{name}".'
                    'Make sure you define "tags" in correct way.'
                )"""

    def read(self):
        for event_id in self.event_ids:
            yield self.read_one(event_id)

    def read_all(self):
        return [
            self.read_one(event_id) for event_id in self.event_ids
        ]

    def read_one(self, event_id):
        event = Event(event_id=event_id, data={})

        # Read files.
        files = {}
        for name, file_def in self.event_def['files'].items():
            parser = self.parsers[file_def['parser']]
            files[name] = parser(
                self.base_dir / Path(file_def['file'].format(evtid=event_id))
            )

        # Construct dataframe.
        for name, data_def in self.event_def['data'].items():
            dataframes = []
            for file_id, fields in data_def.items():
                dataframes.append(
                    pd.DataFrame(data=files[file_id].extract_fields(
                        fields, self.processors
                    ))
                )
            event.data[name] = pd.concat(dataframes)

        return event

    def __iter__(self):
        self.read()
