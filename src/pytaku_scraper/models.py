from django.contrib.postgres.fields import JSONField
from django.db import models

QUEUE_NAMES = [("Download", "download")]


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
        constraints = [
            models.UniqueConstraint(
                fields=["name", "payload"], name="unique_url_payload"
            )
        ]

    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100, choices=QUEUE_NAMES)
    payload = JSONField(default=dict)

    @classmethod
    def put(cls, name, payload):
        return cls.objects.create(name=name, payload=payload)

    @classmethod
    def put_bulk(cls, name, payloads):
        return cls.objects.bulk_create(
            [cls(name=name, payload=payload) for payload in payloads],
            ignore_conflicts=True,
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


class DownloadResult(models.Model):
    class Meta:
        db_table = "download_result"
        constraints = [
            models.UniqueConstraint(fields=["url", "method"], name="unique_url_method")
        ]

    downloaded_at = models.DateTimeField(auto_now_add=True)

    url = models.CharField(max_length=1024)
    method = models.CharField(max_length=7, default="get")

    resp_body = models.TextField()
    resp_status = models.IntegerField()
