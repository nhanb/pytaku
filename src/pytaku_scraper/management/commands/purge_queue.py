from django.core.management.base import BaseCommand

from pytaku_scraper.commands import purge_queue


class Command(BaseCommand):
    help = "Delete all tasks in a queue."

    def add_arguments(self, parser):
        parser.add_argument("task")

    def handle(self, *args, **options):
        task = options["task"]
        purge_queue(task)
