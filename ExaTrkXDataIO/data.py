#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Any, Dict

import pandas as pd


class Data:
    """
    Output structure of data read by DataReader.

    Use attribute to access metadata and
    use subscript to access containing dataframes.
    """
    def __init__(
        self,
        metadata: Dict[str, Any],
        dataframe: Dict[str, pd.DataFrame]
    ):
        self.metadata = metadata
        self.dataframe = dataframe

    def __getattr__(self, item):
        """
        Get metadata.
        """
        return self.metadata[item]

    def __getitem__(self, item):
        """
        Get dataframe.
        """
        return self.dataframe[item]

    def __repr__(self):
        str_repr = f"\n======Data======\n"

        str_repr += "\nMetadata:\n"
        for field, value in self.metadata.items():
            str_repr += (
                f"{field}: {value}\n"
            )

        str_repr += "\nDataframes:\n"
        for name, data in self.data.items():
            str_repr += (
                f"- {name}: \n{data.head()}\n...\n"
            )
        str_repr += "==================\n"

        return str_repr
