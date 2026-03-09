from django import forms
from django.db import models
from django.utils.translation import gettext_lazy as _

from xprez import constants
from xprez.admin.forms import ModuleForm
from xprez.conf import defaults
from xprez.models.configs import ModuleConfig
from xprez.models.mixins.font_size import FontSizeModuleMixin
from xprez.models.multi_module import MultiModule, MultiModuleItem


class NumbersModule(FontSizeModuleMixin, MultiModule):
    front_cacheable = True
    config_model = "xprez.NumbersConfig"
    front_template_name = "xprez/modules/numbers.html"
    admin_template_name = "xprez/admin/modules/numbers/numbers.html"
    admin_item_template_name = "xprez/admin/modules/numbers/numbers_item.html"
    admin_form_class = "xprez.modules.numbers.NumbersModuleForm"
    admin_icon_template_name = "xprez/shared/icons/modules/numbers.html"

    class Meta:
        verbose_name = "Numbers"

    class FrontMedia:
        js = ("xprez/js/numbers.min.js",)

    def save(self, *args, **kwargs):
        no_initial_item = kwargs.pop("no_initial_item", False)
        is_new = not self.pk
        super().save(*args, **kwargs)
        if is_new and not no_initial_item:
            self.create_item(saved=True)

    def duplicate_to(self, target_section, saved=False, **kwargs):
        kwargs["no_initial_item"] = True
        return super().duplicate_to(target_section, saved=saved, **kwargs)


class NumbersItem(MultiModuleItem):
    module = models.ForeignKey(
        NumbersModule,
        related_name="items",
        on_delete=models.CASCADE,
        editable=False,
    )
    number = models.IntegerField(null=True, blank=True)
    suffix = models.CharField(max_length=10, null=True, blank=True)
    caption = models.CharField(max_length=100, blank=True)

    def number_intcomma(self):
        """Comma-separated thousands."""
        return f"{self.number:,}" if self.number is not None else ""


class NumbersConfig(ModuleConfig):
    admin_template_name = "xprez/admin/configs/modules/numbers.html"

    COLUMNS_CHOICES = (
        (constants.COLUMNS_AUTO, _("Auto")),
        (1, "1"),
        (2, "2"),
        (3, "3"),
        (4, "4"),
        (5, "5"),
        (6, "6"),
        (7, "7"),
        (8, "8"),
    )
    columns = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        choices=COLUMNS_CHOICES,
        default=defaults.XPREZ_DEFAULTS["module_config"]["xprez.NumbersModule"][
            "columns"
        ],
    )

    gap_choice = models.CharField(
        _("Gap"),
        max_length=20,
        choices=constants.GAP_CHOICES,
        default=defaults.XPREZ_DEFAULTS["module_config"]["xprez.NumbersModule"][
            "gap_choice"
        ],
        blank=True,
    )
    gap_custom = models.PositiveIntegerField(null=True, blank=True)

    def get_css_classes(self):
        classes = super().get_css_classes()
        classes["numbers-columns-auto"] = self.columns is self.constants.COLUMNS_AUTO
        return classes

    def get_css_variables(self):
        css_variables = super().get_css_variables()
        css_variables["gap"] = self._get_choice_or_custom("gap")
        if self.columns is not self.constants.COLUMNS_AUTO:
            css_variables["columns"] = self.columns
        return css_variables


class NumbersModuleForm(ModuleForm):
    options_fields = ModuleForm.options_fields + ("font_size",)
