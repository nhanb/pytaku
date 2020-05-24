from django.contrib.postgres.fields import JSONField
from django.db import models

QUEUE_NAMES = [("Scrape", "scrape")]


class TaskQueue(models.Model):
    """
    Simple postgres-backed task queue.
    Supports concurrent consumers thanks to SELECT FOR UPDATE SKIP LOCKED.

    Usage:
        - Create task: TaskQueue.put() or TaskQueue.put_bulk()
        - Consume task:
            with transaction.atomic():
                task = TaskQueue.pop()
                # do work with task
                task.finish()
        - If anything goes wrong between pop() and finish(),
          the task is automatically put back in the queue.
    """

    class Meta:
        db_table = "task_queue"

    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100, choices=QUEUE_NAMES)
    payload = JSONField(default=dict)

    @classmethod
    def put(cls, name, payload):
        return cls.objects.create(name=name, payload=payload)

    @classmethod
    def put_bulk(cls, name, payloads):
        return cls.objects.bulk_create(
            [cls(name=name, payload=payload) for payload in payloads]
        )

    @classmethod
    def pop(cls, name):
        """
        SELECT FOR UPDATE SKIP LOCKED.
        Must be run inside a transaction.

        Remember to call instance.finish() once you're done.
        """
        return (
            TaskQueue.objects.select_for_update(skip_locked=True)
            .filter(name=name)
            .order_by("id")
            .first()
        )

    def finish(self):
        return self.delete()


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
