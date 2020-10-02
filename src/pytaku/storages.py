import textwrap
from abc import ABC, abstractmethod
from pathlib import Path


class Storage(ABC):
    @abstractmethod
    def save(self, path: Path, blob: bytes):
        pass

    @abstractmethod
    def exists(self, path: Path) -> bool:
        pass

    @abstractmethod
    def read(self, path: Path) -> bytes:
        pass


class FilesystemStorage(Storage):
    def save(self, path: Path, blob: bytes):
        path = self._split_long_filename(path)
        if not path.parent.is_dir():
            path.parent.mkdir(parents=True)
        path.write_bytes(blob)

    def exists(self, path: Path) -> bool:
        path = self._split_long_filename(path)
        return path.is_file()

    def read(self, path: Path) -> bytes:
        path = self._split_long_filename(path)
        return path.read_bytes()

    @staticmethod
    def _split_long_filename(path: Path) -> Path:
        filename = path.name
        if len(filename) <= 255:
            return path
        else:
            parts = textwrap.wrap(filename, width=255)
            newpath = path.parent
            for part in parts:
                newpath /= Path(part)
            return newpath


# TODO: support other storages e.g. s3-like
storage = FilesystemStorage()
