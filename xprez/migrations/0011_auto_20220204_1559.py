# Generated by Django 2.2.25 on 2022-02-04 14:59

from django.db import migrations


def fill_css_class(apps, schema_editor):
    MediumEditor = apps.get_model("xprez.MediumEditor")
    CkEditor = apps.get_model("xprez.CkEditor")
    TextImage = apps.get_model("xprez.TextImage")

    for Model in [TextImage, MediumEditor, CkEditor]:
        for obj in Model.objects.all():
            obj.css_class = obj.css_class_old
            obj.save()


def noop(*args, **kwargs):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("xprez", "0010_auto_20220204_1540"),
    ]

    operations = [
        migrations.RunPython(fill_css_class, noop),
    ]
