# Generated by Django 3.1.2 on 2020-10-01 19:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="storageserver",
            name="state",
        ),
        migrations.AddField(
            model_name="storageserver",
            name="status",
            field=models.CharField(
                choices=[("RUNNING", "Running"), ("DOWN", "Down")],
                default="RUNNING",
                max_length=20,
                verbose_name="State of the server",
            ),
        ),
        migrations.AlterField(
            model_name="storageserver",
            name="available_space",
            field=models.IntegerField(verbose_name="Available space on disk, in bytes"),
        ),
        migrations.AlterField(
            model_name="storedfile",
            name="name",
            field=models.TextField(verbose_name="File name"),
        ),
    ]