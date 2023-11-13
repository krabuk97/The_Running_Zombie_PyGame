# -*- coding: utf-8 -*-
from __future__ import annotations

from io import BytesIO, TextIOWrapper
from tarfile import TarInfo
from typing import List, Tuple

import numpy as np
import pandas as pd

from ..base import FlexExtension

try:
    from astropy.io import fits
    from astropy.table import Table
except ImportError:
    fits = Table = None


class TableExtension(FlexExtension):
    """
    An extension that stores data in a pandas table
    The data is stored in the parquet format
    """

    data_extension = "parquet"

    def __init__(self, header=None, data=None, cls=None):
        super().__init__(header=header, cls=cls)
        self.data = data

    @classmethod
    def _prepare_table(cls, name: str, data: pd.DataFrame) -> tuple[TarInfo, BytesIO]:
        """prepare the table data for writing to disk"""
        bio = BytesIO()
        data.to_parquet(bio, index=True)
        info = cls._get_tarinfo_from_bytesio(name, bio)
        return info, bio

    def _prepare(self, name: str) -> list[tuple[TarInfo, BytesIO]]:
        """prepare the extension for writing to disk"""
        cls = self.__class__
        header_fname = f"{name}/header.json"
        data_fname = f"{name}/data.{cls.data_extension}"
        header_info, header_bio = cls._prepare_json(header_fname, self.header)
        data_info, data_bio = cls._prepare_table(data_fname, self.data)

        return [(header_info, header_bio), (data_info, data_bio)]

    @classmethod
    def _parse_table(cls, bio: BytesIO) -> pd.DataFrame:
        """Read the dataframe from disk"""
        b = BytesIO(bio.read())
        data = pd.read_parquet(b)
        return data

    @classmethod
    def _parse(cls, header: dict, members: dict) -> TableExtension:
        """read data from disk"""
        bio = members[f"data.{cls.data_extension}"]
        data = cls._parse_table(bio)
        ext = cls(header=header, data=data)
        return ext

    def to_dict(self) -> dict:
        """convert into a dictionary"""
        obj = {"header": self.header, "data": self.data.to_dict(orient="records")}
        return obj

    @classmethod
    def from_dict(cls, header: dict, data: dict) -> TableExtension:
        """convert from dict to extension"""
        data = pd.DataFrame.from_records(data["data"])
        obj = cls(header, data)
        return obj

    def to_fits(self) -> fits.BinTableHDU:
        """convert to fits extension"""
        header = self._prepare_fits_header()
        table = Table.from_pandas(self.data)
        hdu = fits.BinTableHDU(table, header)
        return hdu

    @classmethod
    def from_fits(cls, header: dict, data: np.ndarray) -> TableExtension:
        """read data from fits"""
        df = Table(data).to_pandas()
        obj = cls(header, df)
        return obj


class AsciiTableExtension(TableExtension):
    """An extension that stores the data in text format on disk"""

    data_extension = "txt"

    @classmethod
    def _prepare_table(cls, name: str, data: pd.DataFrame) -> tuple[TarInfo, BytesIO]:
        """prepare tar info for this table"""
        tio = TextIOWrapper(BytesIO(), "utf-8")
        data.to_csv(tio, index=False)
        bio = tio.detach()
        info = cls._get_tarinfo_from_bytesio(name, bio)
        return info, bio

    @staticmethod
    def _parse_table(bio: BytesIO) -> pd.DataFrame:
        """read table from disk"""
        data = pd.read_csv(bio)
        return data


class JSONTableExtension(TableExtension):
    """An extension that stores a table in json format on disk"""

    data_extension = "json"

    @classmethod
    def _prepare_table(cls, name: str, data: pd.DataFrame) -> tuple[TarInfo, BytesIO]:
        """prepare tar info"""
        tio = TextIOWrapper(BytesIO(), "utf-8")
        data.to_json(tio, orient="records")
        bio = tio.detach()
        info = cls._get_tarinfo_from_bytesio(name, bio)
        return info, bio

    @staticmethod
    def _parse_table(bio: BytesIO) -> pd.DataFrame:
        """read table from disk"""
        data = pd.read_json(bio, orient="records")
        return data
