import requests
from django.core.management.base import BaseCommand
from django.db import transaction

from pytaku_scraper.models import ScrapeAttempt, TaskQueue


class Command(BaseCommand):
    help = "Scrape worker. Run as many as needed."

    def handle(self, *args, **options):
        task_name = "scrape"

        while True:
            with transaction.atomic():
                task = TaskQueue.pop(task_name)
                task_id = task.id
                print(f"Processing task {task_id}: {task.payload}")
                resp = requests.get(task.payload["url"], timeout=30)
                assert resp.status_code in (200, 404), f"Unexpected error: {resp.text}"

                ScrapeAttempt.objects.create(
                    url=task.payload["url"],
                    method="get",  # TODO
                    resp_body=resp.text,
                    resp_status=resp.status_code,
                )

                task.finish()
                print("Done task", task_id)
