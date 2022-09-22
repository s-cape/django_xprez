# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-15 10:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("example_app", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="page",
            name="slug",
            field=models.SlugField(default="a", max_length=255, unique=True),
            preserve_default=False,
        ),
    ]
