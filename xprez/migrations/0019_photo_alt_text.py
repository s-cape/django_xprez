# Generated by Django 2.2.24 on 2022-03-23 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("xprez", "0018_auto_20220312_1845"),
    ]

    operations = [
        migrations.AddField(
            model_name="photo",
            name="alt_text",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
