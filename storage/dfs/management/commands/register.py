import logging

from dfs.settings import HOST_IP, HOST_NAMING, HOST_PORT, WORK_DIR
from dfs.utils import create_workdir, registry
from django.core.management.base import BaseCommand

logger = logging.getLogger("common")


class Command(BaseCommand):
    help = "Checks health of storage servers"

    def handle(self, *args, **kwargs):
        logger.info("Initialize registration")
        # REGISTRY
        registry(HOST_NAMING, HOST_IP, HOST_PORT)
        create_workdir(WORK_DIR)

        logger.info("Finish registration")
