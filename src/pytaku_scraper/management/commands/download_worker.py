from django.core.management.base import BaseCommand

from pytaku_scraper.commands import download_worker


class Command(BaseCommand):
    help = "Download worker. Run as many as needed."

    def handle(self, *args, **options):
        download_worker()
