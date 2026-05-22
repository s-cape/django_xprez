from django.db import migrations
from xprez.migrations._refactor_0_3_0 import ContentsContainerToContainer


class Migration(migrations.Migration):
    dependencies = [
        ("example_app", "0002_page_slug"),
        ("xprez", "0028_refactor_migrate"),
    ]

    run_before = [("xprez", "0029_refactor_process_modules")]

    operations = [
        ContentsContainerToContainer("Page"),
    ]
