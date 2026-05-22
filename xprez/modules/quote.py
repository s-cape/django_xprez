from django.db import models
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _

from xprez import constants
from xprez.admin.forms import ModuleForm
from xprez.models.mixins.font_size import FontSizeModuleMixin
from xprez.models.modules import Module
from xprez.utils import truncate_with_ellipsis


class QuoteModule(FontSizeModuleMixin, Module):
    front_cacheable = True
    front_template_name = "xprez/modules/quote.html"
    admin_template_name = "xprez/admin/modules/quote.html"
    admin_form_class = "xprez.modules.quote.QuoteModuleForm"
    admin_icon_template_name = "xprez/shared/icons/modules/quote.html"

    name = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to="quotes", null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    quote = models.TextField()

    class Meta:
        verbose_name = _("Quote")

    def preview_text(self):
        truncated_quote = truncate_with_ellipsis(
            strip_tags(self.quote), constants.PREVIEW_TEXT_MAX_LENGTH
        )
        if self.name:
            return f"{self.name}: {truncated_quote}"
        else:
            return truncated_quote


class QuoteModuleForm(ModuleForm):
    options_fields = ModuleForm.options_fields + ("font_size",)

    class Meta:
        model = QuoteModule
        fields = "__all__"
