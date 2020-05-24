from django.core.management.base import BaseCommand

from pytaku_scraper.models import TaskQueue


class Command(BaseCommand):
    help = "Puts various tasks."

    def add_arguments(self, parser):
        parser.add_argument("task", choices=["scrape"])
        parser.add_argument("start_id", type=int)
        parser.add_argument("end_id", type=int)

    def handle(self, *args, **options):
        assert options["task"] == "scrape"

        result = TaskQueue.put_bulk(
            "scrape",
            [
                {"url": f"https://mangadex.org/api/?type=manga&id={i}"}
                for i in range(options["start_id"], options["end_id"] + 1)
            ],
        )

        print("Result:", result)
