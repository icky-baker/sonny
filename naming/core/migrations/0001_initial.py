# Generated by Django 3.1.2 on 2020-10-01 17:49

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="StorageServer",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "host",
                    models.TextField(
                        validators=[django.core.validators.validate_ipv4_address], verbose_name="IP address"
                    ),
                ),
                ("port", models.IntegerField(verbose_name="port")),
                (
                    "state",
                    models.CharField(
                        choices=[("RUNNING", "Running"), ("DOWN", "Down")], default="RUNNING", max_length=20
                    ),
                ),
                ("available_space", models.IntegerField(verbose_name="Available space on dist, in bytes")),
            ],
            options={
                "unique_together": {("host", "port")},
            },
        ),
        migrations.CreateModel(
            name="StoredFile",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.TextField()),
                ("size", models.IntegerField(verbose_name="Size of the file, in bytes")),
                ("hosts", models.ManyToManyField(related_name="files", to="core.StorageServer")),
            ],
        ),
    ]
