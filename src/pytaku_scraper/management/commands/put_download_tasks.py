from django.core.management.base import BaseCommand

from pytaku_scraper.commands import put_download_tasks


class Command(BaseCommand):
    help = "Puts download tasks for mangadex titles."

    def handle(self, *args, **options):
        put_download_tasks()
