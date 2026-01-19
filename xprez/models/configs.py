from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.template.loader import render_to_string

from xprez import constants
from xprez.conf import settings
from xprez.utils import import_class

BREAKPOINT_CHOICES = tuple(
    [(k, v["name"]) for k, v in settings.XPREZ_BREAKPOINTS.items()]
)


class ConfigParentMixin:
    """Mixin for Section and Module to handle CSS configuration logic."""

    # def config_model(self):
    #     raise NotImplementedError()

    def build_config(self, css_breakpoint):
        raise NotImplementedError()

    def get_configs(self):
        return self.configs.all().order_by("css_breakpoint")

    def get_or_create_config(self, css_breakpoint):
        try:
            return self.get_configs().get(css_breakpoint=css_breakpoint), False
        except ObjectDoesNotExist:
            config = self.build_config(css_breakpoint)
            config.save()
            return config, True

    def get_css(self):
        """Compute changed attributes per breakpoint."""
        configs = self.get_configs().filter(visible=True)
        current_attrs = self.build_config(settings.XPREZ_DEFAULT_BREAKPOINT).get_css()
        result = {}

        for config in configs:
            attrs = config.get_css()
            changed_css = self._get_changed_css(current_attrs, attrs)
            if changed_css:
                result[config.css_breakpoint] = changed_css
            current_attrs.update(attrs)

        return result

    @staticmethod
    def _get_changed_css(base_css, css):
        changed_css = {}
        for key, value in css.items():
            if value != base_css.get(key):
                changed_css[key] = value
        return changed_css

    @staticmethod
    def _get_css_vars(attrs):
        return "; ".join(f"--x-{k}: {v}" for k, v in attrs.items())

    @staticmethod
    def _get_breakpoint_css(selector, breakpoint, attrs):
        css_vars = ConfigParentMixin._get_css_vars(attrs)
        min_width = settings.XPREZ_BREAKPOINTS[breakpoint]["min_width"]
        breakpoint_css = f"{selector} {{ {css_vars}; }}"
        if not min_width:
            return breakpoint_css
        else:
            return f"@media (min-width: {min_width}px) {{\n{breakpoint_css}\n}}"

    def render_css(self):
        css_data = self.get_css()
        if not css_data:
            return ""

        selector = "#" + self.get_identifier()
        output = []

        for breakpoint, attrs in css_data.items():
            output += [self._get_breakpoint_css(selector, breakpoint, attrs)]

        if output:
            return "<style>\n" + "\n".join(output) + "\n</style>"
        else:
            return ""


class ConfigBase(models.Model):
    css_breakpoint = models.PositiveSmallIntegerField(
        choices=BREAKPOINT_CHOICES,
        default=settings.XPREZ_DEFAULT_BREAKPOINT,
        editable=False,
    )

    def is_default(self):
        return self.css_breakpoint == settings.XPREZ_DEFAULT_BREAKPOINT

    def get_admin_form_class(self):
        return import_class(self.form_class)

    def build_admin_form(self, admin, data=None, files=None):
        form_class = self.get_admin_form_class()

        self.admin_form = form_class(
            instance=self, prefix=self.get_identifier(), data=data, files=files
        )
        self.admin_form.xprez_admin = admin

    def is_admin_form_valid(self):
        return self.admin_form.is_valid()

    def save_admin_form(self, request):
        inst = self.admin_form.save(commit=False)
        inst.save()

    def render_admin(self, context):
        context["config"] = self
        return render_to_string(self.admin_template_name, context)

    def get_css(self):
        raise NotImplementedError()

    def _get_choice_or_custom(self, field_prefix, custom_formatter=None):
        choice_value = getattr(self, f"{field_prefix}_choice")
        if choice_value != constants.CUSTOM:
            return choice_value
        else:
            custom_value = getattr(self, f"{field_prefix}_custom")
            return self._format(custom_formatter, custom_value)

    @staticmethod
    def _format(formatter, value):
        if formatter:
            if isinstance(formatter, str):
                return formatter.format(value)
            else:
                return formatter(value)
        else:
            return value

    class Meta:
        abstract = True


class SectionConfig(ConfigBase):
    admin_template_name = "xprez/admin/configs/section.html"
    form_class = "xprez.admin.forms.SectionConfigForm"

    section = models.ForeignKey(
        "xprez.Section",
        on_delete=models.CASCADE,
        related_name="configs",
        editable=False,
    )
    visible = models.BooleanField(default=True)

    margin_bottom_choice = models.CharField(
        "Margin bottom",
        max_length=20,
        choices=constants.MARGIN_CHOICES,
        default=constants.MARGIN_MEDIUM,
    )
    margin_bottom_custom = models.PositiveIntegerField(null=True, blank=True)

    padding_left_choice = models.CharField(
        "Padding left",
        max_length=20,
        choices=constants.PADDING_CHOICES,
        default=constants.PADDING_NONE,
    )
    padding_right_choice = models.CharField(
        "Padding right",
        max_length=20,
        choices=constants.PADDING_CHOICES,
        default=constants.PADDING_NONE,
    )
    padding_top_choice = models.CharField(
        "Padding top",
        max_length=20,
        choices=constants.PADDING_CHOICES,
        default=constants.PADDING_NONE,
    )
    padding_bottom_choice = models.CharField(
        "Padding bottom",
        max_length=20,
        choices=constants.PADDING_CHOICES,
        default=constants.PADDING_NONE,
    )
    padding_left_custom = models.PositiveIntegerField(null=True, blank=True)
    padding_right_custom = models.PositiveIntegerField(null=True, blank=True)
    padding_top_custom = models.PositiveIntegerField(null=True, blank=True)
    padding_bottom_custom = models.PositiveIntegerField(null=True, blank=True)
    padding_x_linked = models.BooleanField(default=True)
    padding_y_linked = models.BooleanField(default=True)

    COLUMN_CHOICES = [(i, str(i)) for i in range(1, 8)]
    columns = models.PositiveSmallIntegerField(choices=COLUMN_CHOICES, default=1)

    gap_choice = models.CharField(
        "Gap",
        max_length=20,
        choices=constants.GAP_CHOICES,
        default=constants.GAP_FULL,
    )
    gap_custom = models.PositiveIntegerField(null=True, blank=True)

    vertical_align = models.CharField(
        max_length=20,
        choices=constants.VERTICAL_ALIGN_CHOICES,
        default=constants.VERTICAL_ALIGN_TOP,
    )

    horizontal_align = models.CharField(
        max_length=20,
        choices=constants.HORIZONTAL_ALIGN_CHOICES,
        default=constants.HORIZONTAL_ALIGN_LEFT,
    )

    def get_css(self):
        return {
            "columns": self.columns,
            "margin-bottom": self._get_choice_or_custom(
                "margin_bottom", "{}" + constants.MARGIN_CUSTOM_UNITS
            ),
            "padding-left": self._get_choice_or_custom(
                "padding_left", "{}" + constants.PADDING_CUSTOM_UNITS
            ),
            "padding-right": self._get_choice_or_custom(
                "padding_right", "{}" + constants.PADDING_CUSTOM_UNITS
            ),
            "padding-top": self._get_choice_or_custom(
                "padding_top", "{}" + constants.PADDING_CUSTOM_UNITS
            ),
            "padding-bottom": self._get_choice_or_custom(
                "padding_bottom", "{}" + constants.PADDING_CUSTOM_UNITS
            ),
            "gap": self._get_choice_or_custom("gap", "{}" + constants.GAP_CUSTOM_UNITS),
            "vertical-align": self.vertical_align,
            "horizontal-align": self.horizontal_align,
        }

    def get_identifier(self):
        return "section-config-" + str(self.pk)

    class Meta:
        verbose_name = "Section Config"
        verbose_name_plural = "Section Configs"
        unique_together = ("section", "css_breakpoint")
        ordering = ("css_breakpoint",)


class ModuleConfig(ConfigBase):
    admin_template_name = "xprez/admin/configs/module_base.html"
    form_class = "xprez.admin.forms.ModuleConfigForm"

    module = models.ForeignKey(
        "xprez.Module",
        on_delete=models.CASCADE,
        related_name="configs",
        editable=False,
    )
    visible = models.BooleanField(default=True)

    colspan = models.PositiveSmallIntegerField("Column span", default=1)
    rowspan = models.PositiveSmallIntegerField("Row span", default=1)
    vertical_align = models.CharField(
        max_length=20,
        choices=constants.VERTICAL_ALIGN_CHOICES,
        default=constants.VERTICAL_ALIGN_TOP,
    )
    horizontal_align = models.CharField(
        max_length=20,
        choices=constants.HORIZONTAL_ALIGN_CHOICES,
        default=constants.HORIZONTAL_ALIGN_LEFT,
    )

    def get_css(self):
        return {
            "colspan": self.colspan,
            "rowspan": self.rowspan,
            "vertical-align": self.vertical_align,
            "horizontal-align": self.horizontal_align,
        }

    def get_admin_form_class(self):
        cls = super().get_admin_form_class()
        if cls._meta.model:
            return cls
        else:

            class ModuleConfigForm(cls):
                class Meta(cls.Meta):
                    model = self.__class__

            return ModuleConfigForm

    def get_identifier(self):
        return "module-config-" + str(self.pk)

    class Meta:
        verbose_name = "Module Config"
        verbose_name_plural = "Module Configs"
        unique_together = ("module", "css_breakpoint")
        ordering = ("css_breakpoint",)
