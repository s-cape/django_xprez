import importlib

from django.db import migrations

from xprez.migrations._refactor_0_3_0 import BUILTIN_PROCESSORS


def process_modules(apps, schema_editor):
    all_processors = dict(BUILTIN_PROCESSORS)
    Module = apps.get_model("xprez", "Module")
    modules = list(Module.objects.all())
    for app_label in {m.content_type.split(".")[0] for m in modules} - {"xprez"}:
        mod = importlib.import_module(f"{app_label}.migrations._xprez_refactor_0_3_0")
        all_processors.update(mod.PROCESSORS)
    for module_base in modules:
        all_processors[module_base.content_type](apps, module_base).process()


class Migration(migrations.Migration):
    dependencies = [
        ("xprez", "0028_refactor_migrate"),
    ]

    operations = [
        migrations.RunPython(process_modules, migrations.RunPython.noop),
    ]
