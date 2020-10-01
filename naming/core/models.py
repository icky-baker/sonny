from typing import List

from core.utils.hashes import get_random_hash
from django.core.validators import validate_ipv4_address
from django.db import models
from django.db.models import QuerySet


class StorageServerManager(models.Manager):
    def get_active(self) -> QuerySet:
        return self.filter(status=StorageServer.StorageServerStatuses.RUNNING)

    def allocate(self, file: "StoredFile") -> List["StorageServer"]:
        servers = self.get_active().filter(available_space__gt=file.size).order_by("available_space")
        # let's pick server with the greatest amount of free space
        best_server = servers.first()
        if not best_server:
            # no servers in database
            raise ValueError("No servers available")

        file.hosts.add(best_server)
        file.save()
        return [
            best_server,
        ]


class StorageServer(models.Model):
    class StorageServerStatuses(models.TextChoices):
        RUNNING = "RUNNING"
        DOWN = "DOWN"

    class Meta:
        unique_together = (
            "host",
            "port",
        )

    objects = StorageServerManager()

    host = models.TextField(verbose_name="IP address", validators=(validate_ipv4_address,))
    port = models.IntegerField(verbose_name="port")

    status = models.CharField(
        choices=StorageServerStatuses.choices,
        default=StorageServerStatuses.RUNNING,
        max_length=20,
        verbose_name="State of the server",
    )

    available_space = models.IntegerField(verbose_name="Available space on disk, in bytes")

    def update(self, save: bool = True, **kwargs):
        for name, value in kwargs.items():
            if not hasattr(self, name):
                raise ValueError(f"Unknown field {name}")

            setattr(self, name, value)

        if save:
            self.save()


# todo: make ManyToMany field via an additional table with amount of chunks on every server
# inside the relation. For now, we assume all chunks are placed on one host
class StoredFile(models.Model):
    hosts = models.ManyToManyField(StorageServer, related_name="files")

    name = models.TextField(verbose_name="File name")
    size = models.IntegerField(verbose_name="Size of the file, in bytes")

    owner_hash = models.TextField(
        max_length="10",
        default=get_random_hash,
        verbose_name="Unique hash, only owner of the file knows it",
        editable=False,
    )


__all__ = [StorageServer, StoredFile]
