# Generated by Django 4.2.5 on 2023-10-28 23:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("course", "0009_uploadvideo_duration"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="uploadvideo",
            name="duration",
        ),
    ]