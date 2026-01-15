from django import forms
from django.db import models
from django.forms import inlineformset_factory

from xprez.admin.forms import BaseModuleForm
from xprez.models.modules import MultiModule, MultiModuleItem


class NumbersModule(MultiModule):
    admin_template_name = "xprez/admin/modules/numbers.html"
    front_template_name = "xprez/modules/numbers.html"
    icon_template_name = "xprez/admin/icons/modules/numbers.html"
    form_class = "xprez.modules.numbers.NumbersModuleForm"
    formset_factory = "xprez.modules.numbers.NumbersItemFormSet"

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
    title = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ("module", "id")


class NumbersModuleForm(BaseModuleForm):
    class Meta:
        model = NumbersModule
        fields = BaseModuleForm.base_module_fields


class NumbersItemForm(forms.ModelForm):
    class Meta:
        model = NumbersItem
        widgets = {
            "number": forms.NumberInput(attrs={"class": "short"}),
            "suffix": forms.TextInput(attrs={"class": "short"}),
        }
        fields = (
            "id",
            "number",
            "suffix",
            "title",
        )


NumbersItemFormSet = inlineformset_factory(
    NumbersModule,
    NumbersItem,
    form=NumbersItemForm,
    fields=("id", "number", "suffix", "title"),
    max_num=4,
    extra=4,
    can_delete=True,
)
