# Generated by Django 2.2.25 on 2022-02-04 15:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("xprez", "0011_auto_20220204_1559"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="mediumeditor",
            name="css_class_old",
        ),
        migrations.RemoveField(
            model_name="textimage",
            name="css_class_old",
        ),
    ]
