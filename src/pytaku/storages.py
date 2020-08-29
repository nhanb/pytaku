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
        if not path.parent.is_dir():
            path.parent.mkdir(parents=True)
        path.write_bytes(blob)

    def exists(self, path: Path) -> bool:
        return path.is_file()

    def read(self, path: Path) -> bytes:
        return path.read_bytes()


# TODO: support other storages e.g. s3-like
storage = FilesystemStorage()
