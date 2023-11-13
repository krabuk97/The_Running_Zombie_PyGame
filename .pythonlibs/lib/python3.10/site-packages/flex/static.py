# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd

from .extensions.bindata import BinaryDataExtension
from .extensions.tabledata import TableExtension
from .flex import FlexFile


def write(filename: str, **data):
    header = {}
    extensions = {}
    for key, value in data.items():
        if type(value) is np.ndarray:
            extensions[key] = BinaryDataExtension(data=value)
        elif isinstance(value, pd.DataFrame):
            extensions[key] = TableExtension(data=value)
        else:
            header[key] = value

    ff = FlexFile(header=header, extensions=extensions)
    ff.write(filename)


def read(filename: str) -> FlexFile:
    return FlexFile.read(filename)
