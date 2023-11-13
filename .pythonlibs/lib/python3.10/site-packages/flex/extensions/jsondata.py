# -*- coding: utf-8 -*-
from __future__ import annotations

from tarfile import TarInfo
from typing import BinaryIO, Tuple

from ..base import FlexExtension


class JsonDataExtension(FlexExtension):
    """An extension to store simple json data"""

    def __init__(self, header=None, data=None, cls=None):
        super().__init__(header=header, cls=cls)
        self.data = data

    def _prepare(self, name: str) -> tuple[tuple[TarInfo, BinaryIO]]:
        cls = self.__class__
        header_fname = f"{name}/header.json"
        data_fname = f"{name}/data.json"
        header_info, header_bio = cls._prepare_json(header_fname, self.header)
        data_info, data_bio = cls._prepare_json(data_fname, self.data)
        return [(header_info, header_bio), (data_info, data_bio)]

    @classmethod
    def _parse(cls, header: dict, members: dict) -> JsonDataExtension:
        try:
            bio = members["data.json"]
            data = cls._parse_json(bio)
        except KeyError:
            print("WARNING: No data found in JSON extension")
            data = {}
        ext = cls(header=header, data=data)
        return ext

    def to_dict(self) -> dict:
        """Convert this extension to a dict"""
        obj = {"header": self.header, "data": self.data}
        return obj

    @classmethod
    def from_dict(cls, header: dict, data: dict) -> JsonDataExtension:
        """Load this extension from a dict"""
        arr = data["data"]
        obj = cls(header, arr)
        return obj
