from django.db import models
from django.utils.translation import gettext_lazy as _

from xprez.models.containers import Container


class TemplateContainer(Container):
    """Persistent library of reusable content; can be copied into any container."""

    key = models.SlugField(
        blank=True, default="", max_length=50, unique=True, verbose_name=_("Key")
    )
    image = models.ImageField(
        upload_to="xprez/templates/", blank=True, null=True, verbose_name=_("Image")
    )
    description = models.TextField(
        blank=True, default="", verbose_name=_("Description")
    )
    keywords = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Keywords"),
        help_text=_("Comma-separated keywords"),
    )

    class Meta:
        verbose_name = _("Template")
        verbose_name_plural = _("Templates")
        ordering = ("key",)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.key:
            self.key = self._next_auto_key()
            super().save(update_fields=["key"])

    def _next_auto_key(self):
        existing = TemplateContainer.objects.filter(key__regex=r"^\d+$").values_list(
            "key", flat=True
        )
        next_num = max((int(k) for k in existing), default=0) + 1
        return str(next_num).zfill(4)

    @property
    def display_key(self):
        return f"#{self.key}"

    def __str__(self):
        return self.display_key
