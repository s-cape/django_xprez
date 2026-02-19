from django import forms
from django.db import models

from xprez.admin.forms import ModuleForm, MultiModuleItemForm
from xprez.models.modules import FontSizeModuleMixin, MultiModule, MultiModuleItem


class NumbersModule(FontSizeModuleMixin, MultiModule):
    front_template_name = "xprez/modules/numbers.html"
    admin_template_name = "xprez/admin/modules/numbers/numbers.html"
    admin_item_template_name = "xprez/admin/modules/numbers/numbers_item.html"
    admin_form_class = "xprez.modules.numbers.NumbersModuleForm"
    admin_item_form_class = "xprez.modules.numbers.NumbersItemForm"
    admin_icon_template_name = "xprez/admin/icons/modules/numbers.html"

    class Meta:
        verbose_name = "Numbers"

    class FrontMedia:
        js = (
            "xprez/libs/jquery.waypoints.min.js",
            "xprez/libs/counter.up/jquery.counterup.js",
            "xprez/js/numbers.js",
        )


class NumbersItem(MultiModuleItem):
    module = models.ForeignKey(
        NumbersModule, related_name="items", on_delete=models.CASCADE
    )
    number = models.IntegerField(null=True, blank=True)
    suffix = models.CharField(max_length=10, null=True, blank=True)
    caption = models.CharField(max_length=100, blank=True)


class NumbersModuleForm(ModuleForm):
    options_fields = ModuleForm.options_fields + ("font_size",)


class NumbersItemForm(MultiModuleItemForm):
    class Meta:
        model = NumbersItem
        fields = ("number", "suffix", "caption")
        widgets = {
            "number": forms.NumberInput(attrs={"class": "short"}),
            "suffix": forms.TextInput(attrs={"class": "short"}),
        }
