from django.apps import apps
from django.utils.functional import cached_property


class PolymorphMixin:
    """Shared polymorph resolution for models that store content_type as 'app.Model'."""

    @cached_property
    def polymorph(self):
        app_label, object_name = self.content_type.split(".")
        model = apps.get_model(app_label, object_name)
        if isinstance(self, model):
            return self
        else:
            return model.objects.get(pk=self.pk)
