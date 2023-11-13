# -*- coding: utf-8 -*-
"""
FLEX - The flexible file format

A flex file is a tar file, containing of a header,
and any number of extensions. Each extension contains its own header
and usually some data files.
The header files are json files, with additional conversions to
make them more convenient.

@author Ansgar Wehrhahn
@email ansgar.wehrhahn@physics.uu.se
"""
from __future__ import annotations

import importlib
import json
import tarfile
from tarfile import TarFile
from threading import Thread
from typing import Any

import numpy as np

from . import __version__
from .base import FlexBase, FlexExtension
from .extensions.bindata import BinaryDataExtension
from .extensions.jsondata import JsonDataExtension
from .extensions.tabledata import TableExtension
from .json_encoder import FlexJSONDecoder, FlexJSONEncoder

try:
    from astropy.io import fits
except ImportError:
    fits = None

FITS_EXTENSION = {
    fits.BinTableHDU: TableExtension,
    fits.ImageHDU: BinaryDataExtension,
}


class FlexFile(FlexBase):
    """
    The Flex file that contains it all,
    handles reading and writing of the data
    """

    def __init__(
        self,
        header: dict = None,
        extensions: dict[str, FlexExtension] = None,
        fileobj: TarFile = None,
    ):
        # dict: Header dictionary with any data
        self.header: dict[str, Any] = header if header is not None else {}
        # dict: Extensions contained within this file
        self.extensions: dict[str:FlexExtension] = (
            extensions if extensions is not None else {}
        )
        # TarFile: The fileobject that this object represents
        self.fileobj: TarFile = fileobj
        self.header["__version__"] = __version__
        self.header["__header__"] = True

    def __getitem__(self, key: str) -> FlexExtension:
        return self.extensions[key]

    def __setitem__(self, key: str, value: FlexExtension):
        self.extensions[key] = value

    def write(self, fname: str, compression: bool = False):
        """
        Write this file including all extensions to disk

        Parameters
        ----------
        fname : str
            Location at which to store the file
        compression : bool, optional
            Whether to compress the file, by default False

        Raises
        ------
        ValueError
            An extension could not be saved
        """
        # Write the header
        cls = self.__class__
        # Update header with current metadata
        self.header["__version__"] = __version__
        self.header["__header__"] = True

        info, bio = cls._prepare_json("header.json", self.header)
        extensions = []
        for name, ext in self.extensions.items():
            if isinstance(ext, FlexExtension):
                extensions += ext._prepare(name)
            elif hasattr(ext, "__flex_save__"):
                extensions += ext.__flex_save__()
            elif hasattr(ext, "to_dict"):
                extensions += JsonDataExtension(
                    data=ext.to_dict(),
                    cls=f"{ext.__class__.__module__}.{ext.__class__.__name__}",
                )
            else:
                raise ValueError(f"Could not save extension {name}")

        mode = "w:" if not compression else "w:gz"
        with tarfile.open(fname, mode) as file:
            file.addfile(info, bio)
            for ext in extensions:
                file.addfile(ext[0], ext[1])

    def write_async(self, fname: str, compression: bool = False):
        """
        !EXPERIMENTAL
        Write data to disk async, only works if this file is
        not manipulated until the operation is finished.
        """
        worker = Thread(
            target=self.write, args=(fname,), kwargs={"compression": compression}
        )
        worker.daemon = True
        worker.start()

    @classmethod
    def _read_ext_class(cls, ext_header: dict) -> type[FlexExtension]:
        """Determine and load the class that created this extension"""
        ext_module = ext_header["__module__"]
        ext_class = ext_header["__class__"]
        ext_module = importlib.import_module(ext_module)
        ext_class = getattr(ext_module, ext_class)
        return ext_class

    @classmethod
    def read(cls, fname: str, mmap: bool = False) -> FlexFile:
        """
        Read a flex file from disk

        Parameters
        ----------
        fname : str
            Filename of the file to load
        mmap : bool, optional
            Whether to memory map the file. This means that the file will
            not be read into working memory, until that bit is accessed.
            Useful for large datafiles, but only works with uncompressed files.
            By default False.

        Returns
        -------
        FlexFile
            The read file

        Raises
        ------
        ValueError
            If any extension could not be read
        """
        handle = open(fname, "rb")
        # If we allow mmap.ACCESS_WRITE, we invalidate the checksum
        # So I think the best solution is to use COPY
        # This also prevents the user accidentially messing up the files
        if mmap:
            mapped = mmap.mmap(handle.fileno(), 0, access=mmap.ACCESS_COPY)
            file = tarfile.open(mode="r", fileobj=mapped)
        else:
            file = tarfile.open(fname, mode="r")

        header = cls._read_json(file, "header.json")

        names = file.getnames()
        names = np.array([n for n in names if n != "header.json"])
        if len(names) != 0:
            # If the file was created using Windows style paths
            ext = np.char.replace(names, "\\", "/")
            ext = np.char.partition(ext, "/")
            ext = ext[:, 0]
            ext, mapping = np.unique(ext, return_inverse=True)
        else:
            ext, mapping = [], None

        extensions = {}
        for i, name in enumerate(ext):
            # Determine the files contributing to this extension
            members = names[mapping == i]
            ext_header = ""
            ext_other = []
            for n in members:
                if n.endswith("header.json"):
                    ext_header = n
                else:
                    ext_other += [n]

            # Determine the extension class and module
            ext_header = cls._read_json(file, ext_header)
            ext_class = cls._read_ext_class(ext_header)

            # TODO: lazy load the extensions?
            ext_other = {
                other[len(name) + 1 :]: file.extractfile(other) for other in ext_other
            }
            if issubclass(ext_class, FlexExtension):
                exten = ext_class._parse(ext_header, ext_other)
            elif hasattr(ext_class, "__flex_load__"):
                exten = ext_class.__flex_load__(ext_header, ext_other)
            elif hasattr(ext_class, "from_dict"):
                temp_exten = JsonDataExtension._parse(ext_header, ext_other)
                exten = ext_class.from_dict(temp_exten.data)
            else:
                raise ValueError(f"Could not decode extension {name}")

            extensions[name] = exten

        return cls(header=header, extensions=extensions, fileobj=file)

    def close(self):
        """Close this file"""
        if self.fileobj is not None:
            self.fileobj.fileobj.close()
            self.fileobj.close()

    def to_dict(self) -> dict:
        """
        Create a dictionary representation of this file.
        Each extension handles the conversion itself.
        """
        obj = {"header": self.header}
        for name, ext in self.extensions.items():
            obj[name] = ext.to_dict()
        return obj

    @classmethod
    def from_dict(cls, data: dict) -> FlexFile:
        """
        Load data from a dictionary

        Parameters
        ----------
        data : dict
            The data to parse

        Returns
        -------
        FlexFile
            The created flex file
        """
        header = {}
        extensions = {}
        for name, ext in data.items():
            if name == "header":
                header = ext
                continue

            ext_header = ext["header"]
            ext_class = cls._read_ext_class(ext_header)
            del ext["header"]
            exten = ext_class.from_dict(ext_header, ext)
            extensions[name] = exten

        obj = cls(header, extensions)
        return obj

    def to_json(self, fp: str = None) -> str:
        """
        Create a json representation of this file.
        This uses the to_dict method of the file,
        and then converts it into a JSON string

        Parameters
        ----------
        fp : str, optional
            If given will store the data at that location

        Returns
        -------
        obj : str
            The json string
        """
        obj = self.to_dict()
        kwargs = dict(cls=FlexJSONEncoder, allow_nan=False, skipkeys=False)
        obj = json.dumps(obj, **kwargs)
        if fp is not None:
            try:
                fp.write(obj)
            except AttributeError:
                with open(fp, "w") as f:
                    f.write(obj)
        return obj

    @classmethod
    def from_json(cls, obj: str) -> FlexFile:
        """
        Read a flex file from a json representation

        Parameters
        ----------
        obj : str
            Json string, or file name

        Returns
        -------
        FlexFile
            The converted flex file
        """
        try:
            obj = json.loads(obj, cls=FlexJSONDecoder)
        except json.decoder.JSONDecodeError:
            # Its already a json string
            with open(obj, "r") as f:
                obj = json.load(f, cls=FlexJSONDecoder)
        obj = cls.from_dict(obj)
        return obj

    def to_fits(self, fname: str | None = None, overwrite: bool = False) -> list[Any]:
        """
        Save this flex file in a fits file format

        Parameters
        ----------
        fname : str, optional
            If given will save the data at this location, by default None
        overwrite : bool, optional
            Whether to overwrite existing data, by default False

        Returns
        -------
        hdulist : List[Any]
            the fits data
        """
        header = self._prepare_fits_header()
        primary = fits.PrimaryHDU(header=header)
        hdus = [primary]
        for ext_name, ext_data in self.extensions.items():
            ext_hdu = ext_data.to_fits()
            ext_hdu.header["EXTNAME"] = ext_name
            hdus += [ext_hdu]

        hdulist = fits.HDUList(hdus)
        if fname is not None:
            hdulist.writeto(fname, overwrite=overwrite)
        return hdulist

    @classmethod
    def from_fits(cls, fname: str) -> FlexFile:
        """
        Read a fits file into a flex file

        Parameters
        ----------
        fname : str
            the file to read

        Returns
        -------
        FlexFile
            the converted flex file
        """
        hdulist = fits.open(fname)
        header = cls._parse_fits_header(hdulist[0].header)
        extensions = {}
        for i in range(1, len(hdulist)):
            hdu = hdulist[i]
            ext_header = cls._parse_fits_header(hdu.header)
            ext_data = hdu.data
            ext_name = ext_header["EXTNAME"]
            try:
                # Try determining the flex class the normal way
                ext_class = cls._read_ext_class(ext_header)
            except KeyError:
                # Otherwise use the default mapping between
                # fits extensions and flex extensions
                ext_class = FITS_EXTENSION[type(hdu)]

            extension = ext_class.from_fits(ext_header, ext_data)
            extensions[ext_name] = extension

        obj = cls(header, extensions)
        return obj
