import requests
from django.conf import settings

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
}


class HttpClient:
    def __init__(self, proxy_index=0):
        proxy_region = settings.GCF_PROXY_REGIONS[proxy_index]
        self.proxy_url = "https://{}-{}.cloudfunctions.net/{}".format(
            proxy_region,
            settings.GCF_PROXY_PROJECT_NAME,
            settings.GCF_PROXY_FUNCTION_NAME,
        )
        print("HttpClient proxy region:", proxy_region)

    def proxied_get(self, url, timeout=10):
        return requests.post(
            self.proxy_url,
            json={
                "url": url,
                "method": "get",
                "body": None,
                "headers": HEADERS,
                "password": settings.GCF_PROXY_PASSWORD,
            },
            timeout=timeout,
        )
