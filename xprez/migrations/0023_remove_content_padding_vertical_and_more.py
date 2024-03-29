# Generated by Django 4.1.4 on 2023-12-21 09:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("xprez", "0022_content_alternate_color_content_background_color_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="content",
            name="padding_vertical",
        ),
        migrations.AddField(
            model_name="content",
            name="padding_bottom",
            field=models.PositiveSmallIntegerField(
                choices=[(0, "None"), (1, "S"), (2, "M"), (3, "L"), (4, "XL")],
                default=0,
            ),
        ),
        migrations.AddField(
            model_name="content",
            name="padding_top",
            field=models.PositiveSmallIntegerField(
                choices=[(0, "None"), (1, "S"), (2, "M"), (3, "L"), (4, "XL")],
                default=0,
            ),
        ),
    ]
