from django import forms
from django.db import models

from xprez.admin.forms import ModuleForm
from xprez.models.modules import FontSizeModuleMixin, Module


class QuoteModule(FontSizeModuleMixin, Module):
    front_template_name = "xprez/modules/quote.html"
    admin_template_name = "xprez/admin/modules/quote.html"
    admin_icon_template_name = "xprez/admin/icons/modules/quote.html"
    admin_form_class = "xprez.modules.quote.QuoteModuleForm"

    name = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to="quotes", null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    quote = models.TextField()

    class Meta:
        verbose_name = "Quote"


class QuoteModuleForm(ModuleForm):
    class Meta:
        model = QuoteModule
        fields = "__all__"
        widgets = {
            "title": forms.TextInput(attrs={"class": "long"}),
            "quote": forms.Textarea(attrs={"class": "long"}),
        }
