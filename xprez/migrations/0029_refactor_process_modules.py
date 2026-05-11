import importlib

from django.db import migrations

from xprez.migrations._refactor_0_3_0 import BUILTIN_PROCESSORS


def _load_processors(modules):
    """
    Collect processors for every content_type present in `modules`.

    Aggregates missing third-party processor modules and unknown content_types
    into a single RuntimeError so admins see the full list of issues at once
    instead of one KeyError/ImportError at a time.
    """
    all_processors = dict(BUILTIN_PROCESSORS)
    apps_with_missing_module = set()

    for app_label in {m.content_type.split(".")[0] for m in modules} - {"xprez"}:
        try:
            mod = importlib.import_module(
                f"{app_label}.migrations._xprez_refactor_0_3_0"
            )
        except ImportError:
            apps_with_missing_module.add(app_label)
            continue
        all_processors.update(getattr(mod, "PROCESSORS", {}))

    # If an app's module is missing, every content_type from that app would also
    # show up as "no processor"; skip those to keep the report focused on the
    # actionable root causes.
    orphan_content_types = sorted(
        {
            m.content_type
            for m in modules
            if m.content_type not in all_processors
            and m.content_type.split(".")[0] not in apps_with_missing_module
        }
    )

    if apps_with_missing_module or orphan_content_types:
        lines = ["Cannot migrate to xprez 0.3.0 (see docs/release_notes/0.3.0.md):"]
        for app_label in sorted(apps_with_missing_module):
            lines += [
                f"  - missing module: {app_label}.migrations._xprez_refactor_0_3_0"
            ]
        for ct in orphan_content_types:
            lines += [f"  - no processor for content_type: {ct}"]
        raise RuntimeError("\n".join(lines))

    return all_processors


def process_modules(apps, schema_editor):
    Module = apps.get_model("xprez", "Module")
    modules = list(Module.objects.all())
    all_processors = _load_processors(modules)
    for module_base in modules:
        all_processors[module_base.content_type](apps, module_base).process()


class Migration(migrations.Migration):
    dependencies = [
        ("xprez", "0028_refactor_migrate"),
    ]

    operations = [
        migrations.RunPython(process_modules, migrations.RunPython.noop),
    ]
