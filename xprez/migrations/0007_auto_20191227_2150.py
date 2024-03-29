# Generated by Django 2.2.3 on 2019-12-27 20:50

from django.db import migrations
from django.db.models import OneToOneRel


def fill_content_type(apps, schema_editor):
    ContentsContainer = apps.get_model("xprez.ContentsContainer")
    attrs = [
        f.name
        for f in ContentsContainer._meta.get_fields()
        if isinstance(f, OneToOneRel)
    ]

    for container in ContentsContainer.objects.all():
        for attr in attrs:
            if hasattr(container, attr):
                container.content_type = attr
                container.save()


class Migration(migrations.Migration):

    dependencies = [
        ("xprez", "0006_contentscontainer_content_type"),
    ]

    operations = [migrations.RunPython(fill_content_type)]
