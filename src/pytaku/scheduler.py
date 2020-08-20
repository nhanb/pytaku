import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

from .persistence import delete_expired_tokens, find_outdated_titles, save_title
from .source_sites import get_title

now = datetime.now


def main_loop():
    workers = [UpdateOutdatedTitles(), DeleteExpiredTokens()]

    while True:
        for worker in workers:
            if worker.should_run():
                print("Running", worker.__class__.__name__)
                worker.run()
                worker.after_run()
        time.sleep(5)


class Worker(ABC):
    interval = timedelta(days=1)

    def __init__(self):
        self.last_run = datetime(1, 1, 1)

    def should_run(self):
        return now() - self.last_run >= self.interval

    @abstractmethod
    def run(self):
        pass

    def after_run(self):
        self.last_run = now()


class UpdateOutdatedTitles(Worker):
    interval = timedelta(hours=2)

    def run(self):
        for title in find_outdated_titles():
            print(f"Updating title {title['id']} from {title['site']}...", end="")
            updated_title = get_title(title["site"], title["id"])
            save_title(updated_title)
            print(" done")


class DeleteExpiredTokens(Worker):
    interval = timedelta(days=1)

    def run(self):
        num_deleted = delete_expired_tokens()
        if num_deleted > 0:
            print("Deleted", num_deleted, "tokens")
