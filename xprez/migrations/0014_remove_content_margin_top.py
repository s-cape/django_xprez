# Generated by Django 2.2.24 on 2022-02-08 12:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('xprez', '0013_merge_20220207_1020'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='content',
            name='margin_top',
        ),
    ]