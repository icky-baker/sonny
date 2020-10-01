from django.core.management.base import BaseCommand
from django.utils import timezone
from models import StorageServer


class Command(BaseCommand):
    help = "Checks health of storage servers"

    def handle(self, *args, **kwargs):
        for server in StorageServer.objects.filter(state=StorageServer.StorageServerStates.RUNNING):
            # TODO: send health request here
            # if no response -> update state to DOWN
            pass
            self.stdout.write("Cron works!!!!!!!!!")
