import logging

import requests
from core.models import StorageServer
from django.core.management.base import BaseCommand

logger = logging.getLogger("common")


class Command(BaseCommand):
    help = "Checks health of storage servers"

    def handle(self, *args, **kwargs):
        for server in StorageServer.objects.all():
            try:
                response = requests.get(f"{server.get_url()}api", timeout=1)
            except (requests.Timeout, requests.ConnectionError):
                response = None

            new_status = None
            if response and response.status_code == 200:
                new_status = StorageServer.StorageServerStatuses.RUNNING
            else:
                new_status = StorageServer.StorageServerStatuses.DOWN

            logger.info(f"Server {server.id} is down")
            server.update(status=new_status)
