from django.contrib.postgres.fields import JSONField
from django.db import models

QUEUE_NAMES = [("Scrape", "scrape")]


class ScrapeAttempt(models.Model):
    class Meta:
        db_table = "scrape_attempt"

    scraped_at = models.DateTimeField(auto_now_add=True)

    url = models.CharField(max_length=1024)
    method = models.CharField(max_length=7)
    headers = JSONField(default=dict)
    body = models.TextField()

    resp_body = models.TextField()
    resp_status = models.IntegerField()


class TaskQueue(models.Model):
    class Meta:
        db_table = "task_queue"

    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100, choices=QUEUE_NAMES)
