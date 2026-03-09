from django.apps import apps
from django.db import models


class ModuleQuerySet(models.QuerySet):
    def polymorphs(self):
        base_modules = list(self.only("content_type"))
        if not base_modules:
            return []

        pks_by_content_type = {}
        for module in base_modules:
            pks_by_content_type.setdefault(module.content_type, []).append(module.pk)

        polymorph_by_pk = {}
        for content_type, pks in pks_by_content_type.items():
            app_label, model_name = content_type.split(".")
            model_class = apps.get_model(app_label, model_name)
            for polymorph in model_class.objects.filter(pk__in=pks):
                polymorph_by_pk[polymorph.pk] = polymorph

        return [polymorph_by_pk[module.pk] for module in base_modules]
