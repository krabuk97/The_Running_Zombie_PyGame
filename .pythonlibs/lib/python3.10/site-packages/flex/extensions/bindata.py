# -*- coding: utf-8 -*-
from __future__ import annotations

import base64
import mmap
from io import BytesIO
from tarfile import TarInfo
from typing import Dict, Tuple

import numpy as np
from numpy.lib.format import _check_version, _read_array_header, read_magic

from ..base import FlexExtension

try:
    from astropy.io import fits
    from astropy.io.fits.column import NUMPY2FITS
except ImportError:
    fits = None


class BinaryDataExtension(FlexExtension):
    """
    Extension that stores binary data
    The data is stored internally using the numpy read and write methods
    """

    def __init__(self, header=None, data=None, cls=None):
        super().__init__(header=header, cls=cls)
        data = data if data is not None else []
        self.data = np.asarray(data)

    @classmethod
    def _prepare_npy(cls, fname: str, data: np.ndarray) -> tuple[TarInfo, BytesIO]:
        """Convert numpy data to tar data"""
        bio = BytesIO()
        np.save(bio, data)
        info = cls._get_tarinfo_from_bytesio(fname, bio)
        return info, bio

    def _prepare(self, name: str) -> tuple[tuple[TarInfo, BytesIO]]:
        """Prepare the extension for writing to disk"""
        cls = self.__class__
        header_fname = f"{name}/header.json"
        data_fname = f"{name}/data.npy"
        header_info, header_bio = cls._prepare_json(header_fname, self.header)
        data_info, data_bio = cls._prepare_npy(data_fname, self.data)

        return [(header_info, header_bio), (data_info, data_bio)]

    @staticmethod
    def _parse_npy(bio: BytesIO) -> np.ndarray:
        """Read numpy data from disk"""
        mmapfile = bio.raw.fileobj
        if isinstance(mmapfile, mmap.mmap):
            version = read_magic(bio)
            _check_version(version)

            shape, fortran_order, dtype = _read_array_header(bio, version)
            if dtype.hasobject:
                msg = "Array can't be memory-mapped: Python objects in dtype."
                raise ValueError(msg)
            order = "F" if fortran_order else "C"
            offset = bio.tell()
            # Add the offset from the Wrapper file
            offset += bio.raw.offset
            data = np.ndarray.__new__(
                np.memmap,
                shape,
                dtype=dtype,
                buffer=mmapfile,
                offset=offset,
                order=order,
            )
            data._mmap = mmapfile
            data.offset = offset
            data.mode = "r+"
        else:
            b = BytesIO(bio.read())
            data = np.load(b)

        return data

    @classmethod
    def _parse(cls, header: dict, members: dict) -> BinaryDataExtension:
        """Read extension data from disk"""
        bio = members["data.npy"]
        data = cls._parse_npy(bio)
        ext = cls(header=header, data=data)
        return ext

    @staticmethod
    def _np_to_dict(data: np.ndarray) -> dict[str, str]:
        """Convert numpy data to a base64 encoded dictionary"""
        encoded = base64.b64encode(data.tobytes())
        encoded = encoded.decode("utf-8")
        obj = {
            "dtype": data.dtype.str,
            "shape": data.shape,
            "order": "C",
            "data": encoded,
        }
        return obj

    @staticmethod
    def _np_from_dict(data: dict[str, str]) -> np.ndarray:
        """Load numpy data from a base64 encoded dict"""
        decoded = data["data"].encode("utf-8")
        decoded = base64.b64decode(decoded)
        arr = np.frombuffer(decoded, dtype=data["dtype"])
        arr = arr.reshape(data["shape"])
        arr = np.require(arr, requirements=["W"])
        return arr

    def to_dict(self) -> dict:
        """convert this extension to a dictionary"""
        cls = self.__class__
        obj = {
            "header": self.header,
            "data": cls._np_to_dict(self.data),
        }
        return obj

    @classmethod
    def from_dict(cls, header: dict, data: dict) -> BinaryDataExtension:
        """Load data from a dictionary"""
        arr = cls._np_from_dict(data["data"])
        obj = cls(header, arr)
        return obj

    @classmethod
    def from_json(cls, header: dict = None, **data: dict) -> BinaryDataExtension:
        """Load data from json dictionary"""
        return cls.from_dict(header, data)

    @staticmethod
    def _prepare_fits_array(value: np.ndarray) -> tuple[str, str, np.ndarray]:
        """Prepare a numpy array for FITS saving"""
        try:
            fits_format = f"{value.dtype.kind}{value.dtype.itemsize}"
            fits_format = NUMPY2FITS[fits_format]
            fits_dim = None
            shape = value.shape
            if len(shape) > 1:
                size = np.prod(value.shape[1:])
                fits_format = "%i%s" % (size, fits_format)
                if len(shape) > 2:
                    fits_dim = str(value.shape[1:][::-1])
        except KeyError:
            fits_format = "D"
            value = value.astype("f8").ravel()
            fits_dim = None
        return fits_format, fits_dim, value

    def to_fits(self) -> fits.FitsHDU:
        """convert the extension to fits format"""
        cls = self.__class__
        header = self._prepare_fits_header()
        fits_format, fits_dim, value = cls._prepare_fits_array(self.data)
        column = fits.Column(name="data", format=fits_format, dim=fits_dim, array=value)
        hdu = fits.BinTableHDU.from_columns([column], header)
        return hdu

    @classmethod
    def from_fits(cls, header: dict, data: dict):
        """read fits data"""
        arr = data["data"]
        obj = cls(header, arr)
        return obj


class MultipleDataExtension(BinaryDataExtension):
    """An extension that can store multiple numpy arrays with different names"""

    def __init__(self, header=None, data=None, cls=None):
        super().__init__(header=header, cls=cls)
        data = data if data is not None else {}
        # dict: data member of this extension
        self.data: dict[str : np.ndarray] = dict(data)

    def __getitem__(self, key: str) -> np.ndarray:
        return self.data[key]

    def __setitem__(self, key: str, value: np.ndarray):
        self.data[key] = value

    def __delitem__(self, key: str):
        del self.data[key]

    def _prepare(self, name: str) -> tuple[tuple[TarInfo, BytesIO]]:
        """prepare this extension for writing to disk"""
        cls = self.__class__

        header_fname = f"{name}/header.json"
        header_info, header_bio = cls._prepare_json(header_fname, self.header)
        result = [(header_info, header_bio)]

        for key, value in self.data.items():
            data_fname = f"{name}/{key}.npy"
            data_info, data_bio = cls._prepare_npy(data_fname, value)
            result += [(data_info, data_bio)]

        return result

    @classmethod
    def _parse(cls, header: dict, members: dict) -> MultipleDataExtension:
        """Read data from flex data"""
        data = {key[:-4]: cls._parse_npy(bio) for key, bio in members.items()}
        ext = cls(header=header, data=data)
        return ext

    def to_dict(self) -> dict:
        """Convert into a dictionary"""
        cls = self.__class__
        obj = {"header": self.header}
        for name, data in self.data.items():
            obj[name] = cls._np_to_dict(data)
        return obj

    @classmethod
    def from_dict(cls, header: dict, data: dict) -> MultipleDataExtension:
        """Convert from a dictionary"""
        data = {name: cls._np_from_dict(d) for name, d in data.items()}
        obj = cls(header, data=data)
        return obj

    def to_fits(self) -> fits.BinTableHDU:
        """convert to fits HDU"""
        cls = self.__class__
        header = self._prepare_fits_header()
        columns = []
        for key, value in self.data.items():
            fits_format, fits_dim, value = cls._prepare_fits_array(value)
            # header["__shape_%s__" % key] = str(value.shape)
            column = fits.Column(
                name=key, format=fits_format, dim=fits_dim, array=value
            )
            columns += [column]
        hdu = fits.BinTableHDU.from_columns(columns, header)
        return hdu

    @classmethod
    def from_fits(cls, header: dict, data: dict) -> MultipleDataExtension:
        """read data from fits data"""
        arr = {name: data[name] for name in data.names}
        obj = cls(header, arr)
        return obj
