from django import forms
from django.db import models

from xprez.admin.forms import BaseModuleForm
from xprez.models.modules import Module


class QuoteModule(Module):
    admin_template_name = "xprez/admin/modules/quote.html"
    front_template_name = "xprez/modules/quote.html"
    icon_template_name = "xprez/admin/icons/modules/quote.html"
    form_class = "xprez.modules.quote.QuoteModuleForm"

    name = models.CharField(max_length=255)
    job_title = models.CharField(max_length=255)
    image = models.ImageField(upload_to="quotes", null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    quote = models.TextField()

    class Meta:
        verbose_name = "Quote"


class QuoteModuleForm(BaseModuleForm):
    class Meta:
        model = QuoteModule
        fields = (
            "name",
            "job_title",
            "title",
            "quote",
            "image",
        ) + BaseModuleForm.base_module_fields
        widgets = {
            "title": forms.TextInput(attrs={"class": "long"}),
            "quote": forms.Textarea(attrs={"class": "long"}),
        }
