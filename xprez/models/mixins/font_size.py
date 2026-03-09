from django.db import models
from django.utils.translation import gettext_lazy as _

from xprez import constants


class FontSizeModuleMixin(models.Model):
    """Mixin that adds font_size field to modules."""

    font_size = models.CharField(
        _("Font size"),
        max_length=20,
        choices=constants.FONT_SIZE_CHOICES,
        default=constants.FONT_SIZE_NORMAL,
    )

    def get_css_classes(self):
        classes = super().get_css_classes()
        if self.font_size != constants.FONT_SIZE_UNSET:
            classes["font-size"] = self.font_size
        return classes

    class Meta:
        abstract = True
