import logging

import requests
from core.models import StorageServer, StoredFile
from django.core.management.base import BaseCommand
from django.forms import model_to_dict

logger = logging.getLogger("common")


class Command(BaseCommand):
    help = "Checks health of storage servers"

    def handle(self, *args, **kwargs):
        print("BLEAT I HATE THIS SHIT")

        logger.info("Starting health check....")
        for server in StorageServer.objects.all():
            logger.info("Check %s", server)
            files_to_replicate = StoredFile.objects.filter(size__lt=server.available_space).exclude(hosts=server)

            try:
                response = requests.post(
                    f"{server.get_url()}api/",
                    timeout=1,
                    data={"files_to_replicate": [model_to_dict(m) for m in files_to_replicate]},
                )
            except (requests.Timeout, requests.ConnectionError):
                response = None

            if response and response.status_code == 200:
                new_status = StorageServer.StorageServerStatuses.RUNNING
            else:
                new_status = StorageServer.StorageServerStatuses.DOWN

            logger.info(f"Server {server.id} new status is {new_status}")
            server.update(status=new_status)
