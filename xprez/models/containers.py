from django.apps import apps
from django.db import models
from django.template.loader import render_to_string
from django.utils.functional import cached_property

from xprez.utils import class_content_type


class Container(models.Model):
    """Base container class for pages/articles that contain modules."""

    front_template_name = "xprez/container.html"

    content_type = models.CharField(max_length=100, editable=False)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.content_type = class_content_type(self.__class__)
        super().save(*args, **kwargs)

    @cached_property
    def polymorph(self):
        app_label, object_name = self.content_type.split(".")
        model = apps.get_model(app_label, object_name)
        if isinstance(self, model):
            return self
        else:
            return model.objects.get(pk=self.pk)

    def copy_modules(self, for_container):
        for module in self.modules.all():
            module.polymorph.copy(for_container)

    def clipboard_verbose_name(self):
        return self.polymorph._meta.verbose_name

    def clipboard_text_preview(self):
        return self.polymorph.__str__()

    def render_front(self, context):
        context["container"] = self.polymorph
        return render_to_string(self.front_template_name, context)

    def get_sections_front(self):
        if not hasattr(self, "_sections_front"):
            self._sections_front = self.sections.filter(saved=True, visible=True)
        return self._sections_front
