# Generated by Django 4.1.4 on 2024-01-03 15:51

from django.db import migrations, models


def migrate_edge_images(apps, schema_editor):
    GridBoxes = apps.get_model("xprez", "GridBoxes")
    GridBoxes.objects.filter(edge_images=True).update(image_sizing="edge")


class Migration(migrations.Migration):
    dependencies = [
        ("xprez", "0023_remove_content_padding_vertical_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="gridboxes",
            name="image_max_width",
            field=models.PositiveSmallIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name="gridboxes",
            name="image_sizing",
            field=models.CharField(
                choices=[("fill", "Default"), ("edge", "Edge"), ("icon", "Icon")],
                default="fill",
                max_length=7,
            ),
        ),
        migrations.RunPython(migrate_edge_images, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="gridboxes",
            name="edge_images",
        ),
    ]