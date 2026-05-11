from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from xprez.models import Module


class AnchorModule(Module):
    front_cacheable = True
    admin_icon_template_name = "xprez/shared/icons/modules/anchor.html"

    title = models.CharField(max_length=100)
    key = models.SlugField(max_length=100, blank=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = slugify(self.title)
        super().save(*args, **kwargs)

    def preview_text(self):
        return self.title

    class Meta:
        verbose_name = _("Anchor")
