#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Any, Dict
from abc import ABC, abstractmethod
from pathlib import Path

import numpy as np

from ..event_data_processor import EventDataProcessor


class EventFileParser(ABC):
    def __init__(self, path):
        self.data = self.load(path)

    def extract_fields(
        self,
        fields: Dict[str, Any],
        processors: Dict[str, EventDataProcessor]
    ) -> Dict[str, np.array]:
        result = {}
        for name, field_def in fields.items():
            if type(field_def) is str:
                result[name] = self.extract(self.data, field_def)
            elif type(field_def) is dict:
                extracted_data = self.extract(self.data, field_def['tag'])
                if 'processing' in field_def:
                    for operation_data in field_def['processing']:
                        # Get processor.
                        processor_id, parameters = list(operation_data.items())[0]
                        processor = processors[processor_id]

                        # Process data.
                        extracted_data = processor.process(
                            extracted_data, **parameters
                        )
                result[name] = extracted_data
        return result

    @abstractmethod
    def load(self, path: Path) -> Any:
        pass

    @abstractmethod
    def extract(self, data, field):
        pass
