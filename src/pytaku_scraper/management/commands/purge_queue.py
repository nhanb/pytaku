from django.core.management.base import BaseCommand

from pytaku_scraper.models import TaskQueue


class Command(BaseCommand):
    help = "Delete all tasks in a queue."

    def add_arguments(self, parser):
        parser.add_argument("task", choices=["scrape"])

    def handle(self, *args, **options):
        task = options["task"]
        assert task == "scrape"

        count, _ = TaskQueue.objects.filter(name=task).delete()
        print(f'Deleted {count} "{task}" tasks.')
