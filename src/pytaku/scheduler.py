import time
import traceback
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from json.decoder import JSONDecodeError
from pathlib import Path

from requests.exceptions import ReadTimeout

from mangoapi.exceptions import SourceSite5xxError

from .conf import config
from .persistence import delete_expired_tokens, find_outdated_titles, save_title
from .source_sites import get_title

now = datetime.now


def main_loop():
    workers = [UpdateOutdatedTitles(), DeleteExpiredTokens(), PruneProxyCache()]

    while True:
        for worker in workers:
            if worker.should_run():
                print("Running", worker.__class__.__name__)
                try:
                    worker.run()
                    worker.after_run()
                except Exception:
                    stacktrace = traceback.format_exc()
                    print(stacktrace)
                    worker.after_error(stacktrace)
        time.sleep(5)


class Worker(ABC):
    interval = timedelta(days=1)

    def __init__(self):
        self.last_run = datetime(1, 1, 1)
        self.error_count = 0

    def should_run(self):
        return now() - self.last_run >= self.interval

    @abstractmethod
    def run(self):
        pass

    def after_run(self):
        self.last_run = now()

    def after_error(self, stacktrace):
        # TODO: email or send stacktrace to an ops chat channel or something
        self.error_count += 1

        # If failed repeatedly: give up this run
        if self.error_count > 3:
            self.last_run = now()
            self.error_count = 0


class UpdateOutdatedTitles(Worker):
    interval = timedelta(hours=2)

    def run(self):
        outdated_titles = find_outdated_titles()
        print(f"Found {len(outdated_titles)} outdated titles")
        for title in outdated_titles:
            print(
                f"Updating title {title['id']} - {title['name'][:36]} from {title['site']}...",
                end="",
            )
            try:
                updated_title = get_title(title["site"], title["id"])
                save_title(updated_title)
                print(" done")
                if title["site"] == "mangasee":
                    time.sleep(2)
            except (SourceSite5xxError, ReadTimeout, JSONDecodeError) as e:
                print(" skipped because of server error:", e.__class__.__name__, str(e))


class DeleteExpiredTokens(Worker):
    interval = timedelta(days=1)

    def run(self):
        num_deleted = delete_expired_tokens()
        if num_deleted > 0:
            print("Deleted", num_deleted, "tokens")


class PruneProxyCache(Worker):
    """
    If proxy cache dir size exceeds config.PROXY_CACHE_MAX_SIZE,
    delete files that are older than config.PROXY_CACHE_MAX_AGE.

    Only applies for FilesystemStorage.
    TODO: update this accordingly when a new Storage class is introduced.
    """

    interval = timedelta(days=1)

    def run(self):
        cache_dir = Path(config.PROXY_CACHE_DIR)
        cache_size = get_dir_size(cache_dir)

        if cache_size <= config.PROXY_CACHE_MAX_SIZE:
            return

        now = time.time()
        files_deleted = 0
        bytes_deleted = 0
        for child in cache_dir.iterdir():
            if child.is_file():
                stat = child.stat()
                modified_at = stat.st_mtime
                if (now - modified_at) > config.PROXY_CACHE_MAX_AGE:
                    child.unlink()  # yes this means delete
                    files_deleted += 1
                    bytes_deleted += stat.st_size

        if files_deleted > 0:
            in_mb = bytes_deleted / 1024 / 1024
            print(f"Deleted {files_deleted} files ({in_mb:.2f} MiB).")
        else:
            print("Deleted nothing.")


def get_dir_size(path: Path):
    """
    In bytes.
    """
    return sum(f.stat().st_size for f in path.glob("**/*") if f.is_file())
