#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Optional
from pathlib import Path
from importlib import import_module
from itertools import product

import pandas as pd
import yaml

from ..data import Data
from .event_file_parser.parsers import (
    NumpyNPZParser,
    PandasCSVParser,
    PyGPickleParser,
    TensorboardLogParser
)
from .event_data_processor.processors import (
    Transpose,
    Select,
    Normalize
)


class DataReader:
    # Default parsers which you don't need to include manually.
    _default_parsers = {
        'numpy.npz': NumpyNPZParser,
        'pandas.csv': PandasCSVParser,
        'pyg.pickle': PyGPickleParser,
        'tb.log': TensorboardLogParser
    }

    # Default processors which you don't need to include manually.
    _default_processors = {
        'transpose': Transpose(),
        'select': Select(),
        'normalize': Normalize()
    }

    # Key words use for special purposes and cannot use as variable key words.
    _keywords = {
        'event': 'event',
        'parsers': 'parsers',
        'processors': 'processors'
    }

    def __init__(self, config_path, base_dir=None):
        """
        Construct data reader.

        :param config_path: Path to yaml configuration.
        :param base_dir: 
            Base directory for your dataset. 
            This will append before file path you specify in configuration file.
        """
        try:
            with open(config_path) as fp:
                self.config = yaml.load(fp, Loader=yaml.SafeLoader)
        except IOError as error:
            raise IOError(
                f"Configuration file cannot be open: {str(config_path)}.\n\n{error}"
            )
        except yaml.YAMLError as error:
            raise yaml.YAMLError(
                f"Cannot parse file as YAML format: {str(config_path)}.\n\n{error}"
            )

        self._set_base_dir(base_dir)
        self._set_variables()
        self._set_parsers()
        self._set_processor()
        self._set_event_def()

    def _set_base_dir(self, base_dir):
        # Set base directory.
        if base_dir is None:
            self.base_dir = None
        else:
            self.base_dir = Path(base_dir)

    def _set_variables(self):
        self.variables = {}

        for name, definition in self.config.items():
            if name not in self._keywords.keys():
                variable = []
                for type, values in definition.items():
                    if type == 'range':
                        variable.extend(list(range(
                            values[0],
                            values[1]
                        )))
                    elif type == 'indices' or type == 'list':
                        variable.extend(values)
                    elif 'constant' in definition:
                        variable.append(values)
                    else:
                        raise SyntaxError(f'Variable {name} not define properly.')

                self.variables[name] = variable

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
                    self.processors[name] = getattr(module, class_name)()

    def _set_event_def(self):
        if 'event' not in self.config:
            raise SyntaxError(
                'Event definition not found.'
                'Make sure you define "event" section in correct way.'
            )

        self.event_def = self.config['event']

        # Early sanity checks.
        # This is a partial check, not include all possible errors.
        if 'files' not in self.event_def:
            print(
                'File definition not found.'
                'If this is not intended, '
                'make sure you define "data" section in correct way'
            )
        else:
            for file_id, file_def in self.event_def['files'].items():
                if 'file' not in file_def:
                    raise SyntaxError(
                        f'File definition not found for {file_id}.'
                        'Make sure you define "file" option in correct way.'
                    )
                if 'parser' not in file_def or file_def['parser'] not in self.parsers:
                    raise AttributeError(
                        f'Parser not found for {file_id}.'
                        'Make sure you define "parser" option in correct way.'
                    )

        if 'data' not in self.event_def:
            print(
                'Data definition not found.'
                'If this is not intended, '
                'make sure you define "data" section in correct way.'
            )
        else:
            for dataframe_id, dataframe_def in self.event_def['data'].items():
                for file_id, fields in dataframe_def.items():
                    for name, field_def in fields.items():
                        if type(field_def) is str:
                            pass
                        elif type(field_def) is dict:
                            if 'tag' not in field_def:
                                raise SyntaxError(
                                    'Tag definition not found.'
                                    'Make sure you define "tag" in correct way.'
                                )
                            if 'processing' in field_def:
                                for operation_data in field_def['processing']:
                                    try:
                                        processor_id, parameters = list(operation_data.items())[0]
                                    except Exception as error:
                                        raise SyntaxError(
                                            f'Processing pipeline for {field_def["tag"]} is not defined properly.'
                                            'Please recheck your pipeline definition.'
                                        )
                                    if processor_id not in self.processors:
                                        raise AttributeError(
                                            f'Processor not found for {field_def["tag"]}.'
                                            'Please recheck your pipeline definition.'
                                        )

    def set_variable(self, key, value: list):
        """
        Set reading parameter with list of values.
        """
        self.variables[key] = value

    def set_constant(self, key, value):
        """
        Set reading parameter with a constant value.
        """
        self.variables[key] = [value]

    def read(self, silent_skip=False):
        """
        Iterate events.

        :param silent_skip: 
            Skip non-exist files without warning. Default is False.
        """
        # FIXME: Unused variables cause duplicated reading progress.

        value_combinations = product(*(self.variables.values()))

        for values in value_combinations:
            kwargs = dict(zip(self.variables.keys(), values))
            data = self.read_one(**kwargs)

            if data is not None:
                yield data
            elif not silent_skip:
                print(f'Event for {kwargs} not find. Skipped.')


    def read_all(self, silent_skip=False):
        """
        Read all events.

        :param silent_skip: 
            Skip non-exist files without warning. Default is False.
        """
        return list(self.read(silent_skip=silent_skip))


    def read_one(self, **kwargs) -> Optional[Data]:
        data = Data(metadata=kwargs, dataframes={})

        # Read files.
        files = {}
        for name, file_def in self.event_def['files'].items():
            parser = self.parsers[file_def['parser']]

            file_path = Path(file_def['file'].format(**kwargs))
            if self.base_dir is not None:
                file_path = self.base_dir / file_path

            if file_path.exists():
                files[name] = parser(file_path)
            else:
                return None

        # Construct dataframe.
        for name, data_def in self.event_def['data'].items():
            dataframes = []
            for file_id, fields in data_def.items():
                dataframes.append(
                    pd.DataFrame(data=files[file_id].extract_fields(
                        fields, self.processors
                    ))
                )
            data.dataframes[name] = pd.concat(dataframes)

        return data

    def __iter__(self):
        self.read()

