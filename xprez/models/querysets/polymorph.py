from django.apps import apps
from django.db import models


class PolymorphQuerySet(models.QuerySet):
    """Queryset of a model that stores its concrete type in ``content_type``."""

    def polymorphs(self):
        """The concrete instances, in order; one query per type."""
        base_objects = list(self.only("content_type"))
        if not base_objects:
            return []

        pks_by_content_type = {}
        for obj in base_objects:
            pks_by_content_type.setdefault(obj.content_type, []).append(obj.pk)

        polymorph_by_pk = {}
        for content_type, pks in pks_by_content_type.items():
            app_label, model_name = content_type.split(".")
            model_class = apps.get_model(app_label, model_name)
            for polymorph in model_class.objects.filter(pk__in=pks):
                polymorph_by_pk[polymorph.pk] = polymorph

        return [
            polymorph_by_pk[obj.pk] for obj in base_objects if obj.pk in polymorph_by_pk
        ]
