# Generated by Django 3.1.2 on 2020-10-06 16:52
from django.contrib.auth.models import User
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0010_auto_20201006_1652"),
    ]

    operations = [
        migrations.RunPython(
            lambda *args: User.objects.create_superuser("+79999999998", password="adminadmin"),
            lambda *args: User.objects.all().delete(),
        )
    ]
