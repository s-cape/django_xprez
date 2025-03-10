import os

from django.db import models

from ..form_fields import RelativeFilePathFieldForm


class TemplatePathField(models.FilePathField):
    def __init__(self, template_dir="", prefix="", **kwargs):
        self.template_dir = template_dir
        self.prefix = prefix
        super().__init__(**kwargs)

    def formfield(self, **kwargs):
        absolute_path = os.path.join(self.template_dir, self.prefix)
        defaults = {
            "path": absolute_path,
            "rel_path": self.prefix,
            "form_class": RelativeFilePathFieldForm,
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)
