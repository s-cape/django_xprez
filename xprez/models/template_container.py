from django.db import models

from xprez.models.containers import Container


class TemplateContainer(Container):
    """Persistent library of reusable content; can be copied into any container."""

    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="xprez/templates/", blank=True, null=True)

    class Meta:
        verbose_name = "Template"
        verbose_name_plural = "Templates"
        ordering = ("name",)

    def __str__(self):
        return self.name
