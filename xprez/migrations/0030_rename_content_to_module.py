# Generated manually for content -> module refactoring
# Note: Model class names are NOT renamed to avoid Django migration issues.
# Python code uses aliases: Module = Content, Container = ContentsContainer, etc.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("xprez", "0029_sections_and_configs_cleanup"),
    ]

    operations = [
        # Rename fields only - no model renames to avoid multi-table inheritance issues
        migrations.RenameField(
            model_name="content",
            old_name="content_type",
            new_name="module_type",
        ),
        migrations.RenameField(
            model_name="contentconfig",
            old_name="content",
            new_name="module",
        ),
        migrations.RenameField(
            model_name="ckeditor",
            old_name="content_centered",
            new_name="module_centered",
        ),
        migrations.RenameField(
            model_name="gridboxes",
            old_name="content_centered",
            new_name="module_centered",
        ),
        migrations.RenameField(
            model_name="quote",
            old_name="content",
            new_name="module",
        ),
        migrations.RenameField(
            model_name="number",
            old_name="content",
            new_name="module",
        ),
        migrations.RenameField(
            model_name="attachment",
            old_name="content",
            new_name="module",
        ),
    ]
