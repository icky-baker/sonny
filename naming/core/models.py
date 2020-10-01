from django.core.validators import validate_ipv4_address
from django.db import models


class StorageServer(models.Model):
    class StorageServerStates(models.TextChoices):
        RUNNING = "RUNNING"
        DOWN = "DOWN"

    class Meta:
        unique_together = (
            "host",
            "port",
        )

    host = models.TextField(verbose_name="IP address", validators=(validate_ipv4_address,))
    port = models.IntegerField(verbose_name="port")

    state = models.CharField(choices=StorageServerStates.choices, default=StorageServerStates.RUNNING, max_length=20)

    def update(self, save: bool = True, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)

        if save:
            self.save()


# todo: make ManyToMany field via an additional table with amount of chunks on every server
# inside the relation. For now, we assume all chunks are placed on one host
class StoredFile(models.Model):
    hosts = models.ManyToManyField(StorageServer, related_name="files")


__all__ = [StorageServer, StoredFile]
