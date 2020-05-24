from django.db import transaction
from django.utils import timezone

from .httpclient import HttpClient
from .models import DownloadResult, TaskQueue
from .sites.mangadex import get_latest_id


def put_download_tasks():
    latest_id = get_latest_id()
    print("Found latest title id:", latest_id)

    result = TaskQueue.put_bulk(
        "download",
        [
            {"url": f"https://mangadex.org/api/?type=manga&id={i}"}
            for i in range(1, latest_id + 1)
        ],
    )
    print(f'Successfully put {len(result)} "download" tasks.')


def download_worker(proxy_index):
    http = HttpClient(proxy_index)
    while True:
        with transaction.atomic():
            task = TaskQueue.pop("download")
            task_id = task.id
            print(f"Processing task {task_id}: {task.payload}")
            resp = http.proxied_get(task.payload["url"])
            assert resp.status_code in (200, 404), f"Unexpected DL error: {resp.text}"

            DownloadResult.objects.update_or_create(
                url=task.payload["url"],
                method="get",
                defaults={
                    "downloaded_at": timezone.now(),
                    "resp_body": resp.text,
                    "resp_status": resp.status_code,
                },
            )

            task.finish()
            print("Done task", task_id)


def purge_queue(task_name):
    count, _ = TaskQueue.objects.filter(name=task_name).delete()
    print(f'Deleted {count} "{task_name}" tasks.')
