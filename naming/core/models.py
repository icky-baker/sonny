from typing import List

from django.core.validators import validate_ipv4_address
from django.db import models
from django.db.models import QuerySet


class StorageServerManager(models.Manager):
    def get_active(self) -> QuerySet:
        return self.filter(status=StorageServer.StorageServerStatuses.RUNNING)

    def get_allocation(self, file: "StoredFile") -> "StorageServer":
        servers = self.get_active().filter(available_space__gt=file.size).order_by("-available_space")
        # let's pick server with the greatest amount of free space
        best_server = servers.first()
        if not best_server:
            # no servers in database
            raise ValueError("No servers available")

        return best_server


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

    available_space = models.PositiveBigIntegerField(verbose_name="Available space on disk, in bytes")

    def update(self, save: bool = True, **kwargs):
        for name, value in kwargs.items():
            if not hasattr(self, name):
                raise ValueError(f"Unknown field {name}")

            setattr(self, name, value)

        if save:
            self.save()

    def get_url(self):
        return f"http://{self.host}:{self.port}/"


class StoredFile(models.Model):
    hosts = models.ManyToManyField(StorageServer, related_name="files")

    name = models.TextField(verbose_name="File name")
    size = models.PositiveBigIntegerField(verbose_name="Size of the file, in bytes", null=True)

    meta = models.JSONField(verbose_name="Meta information about file", null=False, default=dict)

    def is_file(self):
        return self.size is not None

    def is_directory(self):
        return self.size is None

    def get_sub_files(self) -> List["StoredFile"]:
        if not self.is_directory():
            raise ValueError("Not a directory")

        return StoredFile.objects.filter(name__startswith=self.name)


__all__ = [StorageServer, StoredFile]
