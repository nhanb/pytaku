import time
from datetime import datetime, timedelta

from mangoapi import get_title

from .persistence import find_outdated_titles, save_title

now = datetime.now


def main_loop():
    workers = [UpdateOutdatedSeries()]

    while True:
        for worker in workers:
            if worker.should_run():
                print("Running", worker.__class__.__name__)
                worker.run()
                worker.after_run()
        time.sleep(5)


class Worker:
    interval = timedelta(days=1)

    def __init__(self):
        self.last_run = datetime(1, 1, 1)

    def should_run(self):
        return now() - self.last_run >= self.interval

    def run(self):
        raise NotImplementedError()

    def after_run(self):
        self.last_run = now()


class UpdateOutdatedSeries(Worker):
    interval = timedelta(seconds=9)

    def run(self):
        for title in find_outdated_titles():
            print(f"Updating title {title['id']} from {title['site']}...", end="")
            updated_title = get_title(title["id"])
            save_title(updated_title)
            print(" done")
