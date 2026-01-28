from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.template.loader import render_to_string

from xprez import constants
from xprez.conf import settings
from xprez.models.css import CssMixin, CssParentMixin
from xprez.utils import import_class

BREAKPOINT_CHOICES = tuple(
    [(k, v["name"]) for k, v in settings.XPREZ_BREAKPOINTS.items()]
)


class ConfigParentMixin(CssParentMixin):
    """Mixin for Section and Module to handle CSS configuration logic."""

    def build_config(self, css_breakpoint):
        raise NotImplementedError()

    def get_configs(self):
        return self.configs.all().order_by("css_breakpoint")

    def get_or_create_config(self, css_breakpoint):
        try:
            return self.get_configs().get(css_breakpoint=css_breakpoint), False
        except ObjectDoesNotExist:
            previous_config = (
                self.get_configs()
                .filter(css_breakpoint__lt=css_breakpoint)
                .order_by("-css_breakpoint")
                .first()
            )
            if previous_config:
                config = previous_config
                config.pk = None
                config.id = None
                config.css_breakpoint = css_breakpoint
                config.save()
                return config, True
            else:
                config = self.build_config(css_breakpoint)
                config.save()
                return config, True


class ConfigBase(CssMixin, models.Model):
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
            instance=self, prefix=self.key, data=data, files=files
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
        blank=True,
    )
    margin_bottom_custom = models.PositiveIntegerField(null=True, blank=True)

    padding_left_choice = models.CharField(
        "Padding left",
        max_length=20,
        choices=constants.PADDING_CHOICES,
        default=constants.PADDING_SMALL,
        blank=True,
    )
    padding_right_choice = models.CharField(
        "Padding right",
        max_length=20,
        choices=constants.PADDING_CHOICES,
        default=constants.PADDING_SMALL,
        blank=True,
    )
    padding_top_choice = models.CharField(
        "Padding top",
        max_length=20,
        choices=constants.PADDING_CHOICES,
        default=constants.PADDING_NONE,
        blank=True,
    )
    padding_bottom_choice = models.CharField(
        "Padding bottom",
        max_length=20,
        choices=constants.PADDING_CHOICES,
        default=constants.PADDING_NONE,
        blank=True,
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
        default=constants.GAP_SMALL,
        blank=True,
    )
    gap_custom = models.PositiveIntegerField(null=True, blank=True)

    vertical_align_grid = models.CharField(
        max_length=20,
        choices=constants.VERTICAL_ALIGN_GRID_SECTION_CHOICES,
        default=constants.VERTICAL_ALIGN_GRID_STRETCH,
    )

    horizontal_align_grid = models.CharField(
        max_length=20,
        choices=constants.HORIZONTAL_ALIGN_GRID_SECTION_CHOICES,
        default=constants.HORIZONTAL_ALIGN_GRID_STRETCH,
    )

    def get_css(self):
        return {
            "columns": self.columns,
            "margin-bottom": self._get_choice_or_custom("margin_bottom"),
            "padding-left": self._get_choice_or_custom("padding_left"),
            "padding-right": self._get_choice_or_custom("padding_right"),
            "padding-top": self._get_choice_or_custom("padding_top"),
            "padding-bottom": self._get_choice_or_custom("padding_bottom"),
            "gap": self._get_choice_or_custom("gap"),
            "vertical-align-grid": self.vertical_align_grid,
            "horizontal-align-grid": self.horizontal_align_grid,
        }

    def get_css_config_keys(self):
        return ["section_config", "default"]

    @property
    def key(self):
        return f"section-config-{self.pk}"

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

    vertical_align_grid = models.CharField(
        "Vertical align (grid)",
        max_length=20,
        choices=constants.VERTICAL_ALIGN_GRID_MODULE_CHOICES,
        default=constants.VERTICAL_ALIGN_GRID_UNSET,
    )
    horizontal_align_grid = models.CharField(
        "Horizontal align (grid)",
        max_length=20,
        choices=constants.HORIZONTAL_ALIGN_GRID_MODULE_CHOICES,
        default=constants.HORIZONTAL_ALIGN_GRID_UNSET,
    )

    vertical_align_flex = models.CharField(
        "Vertical align (flex)",
        max_length=20,
        choices=constants.VERTICAL_ALIGN_FLEX_CHOICES,
        default=constants.VERTICAL_ALIGN_FLEX_START,
    )
    horizontal_align_flex = models.CharField(
        "Horizontal align (flex)",
        max_length=20,
        choices=constants.HORIZONTAL_ALIGN_FLEX_CHOICES,
        default=constants.HORIZONTAL_ALIGN_FLEX_CENTER,
    )

    background = models.BooleanField(default=False)
    border = models.BooleanField(default=False)

    padding_left_choice = models.CharField(
        "Padding left",
        max_length=20,
        choices=constants.PADDING_CHOICES,
        default=constants.PADDING_NONE,
        blank=True,
    )
    padding_right_choice = models.CharField(
        "Padding right",
        max_length=20,
        choices=constants.PADDING_CHOICES,
        default=constants.PADDING_NONE,
        blank=True,
    )
    padding_top_choice = models.CharField(
        "Padding top",
        max_length=20,
        choices=constants.PADDING_CHOICES,
        default=constants.PADDING_NONE,
        blank=True,
    )
    padding_bottom_choice = models.CharField(
        "Padding bottom",
        max_length=20,
        choices=constants.PADDING_CHOICES,
        default=constants.PADDING_NONE,
        blank=True,
    )
    padding_left_custom = models.PositiveIntegerField(null=True, blank=True)
    padding_right_custom = models.PositiveIntegerField(null=True, blank=True)
    padding_top_custom = models.PositiveIntegerField(null=True, blank=True)
    padding_bottom_custom = models.PositiveIntegerField(null=True, blank=True)
    padding_x_linked = models.BooleanField(default=True)
    padding_y_linked = models.BooleanField(default=True)

    aspect_ratio = models.CharField(max_length=20, blank=True)
    border_radius_choice = models.CharField(
        "Border radius",
        max_length=20,
        choices=constants.BORDER_RADIUS_CHOICES,
        default=constants.BORDER_RADIUS_NONE,
        blank=True,
    )
    border_radius_custom = models.PositiveIntegerField(null=True, blank=True)

    def get_css(self):
        return {
            "colspan": self.colspan,
            "rowspan": self.rowspan,
            "vertical-align-grid": self.vertical_align_grid,
            "horizontal-align-grid": self.horizontal_align_grid,
            "vertical-align-flex": self.vertical_align_flex,
            "horizontal-align-flex": self.horizontal_align_flex,
            "background": int(self.background),
            "border": int(self.border),
            "padding-left": self._get_choice_or_custom("padding_left"),
            "padding-right": self._get_choice_or_custom("padding_right"),
            "padding-top": self._get_choice_or_custom("padding_top"),
            "padding-bottom": self._get_choice_or_custom("padding_bottom"),
            "aspect-ratio": self.aspect_ratio if self.aspect_ratio else "none",
            "border-radius": self._get_choice_or_custom("border_radius"),
        }

    def get_css_config_keys(self):
        return [
            f"module_config.{self.module.content_type}",
            "module_config.default",
            "default",
        ]

    def get_admin_form_class(self):
        cls = super().get_admin_form_class()
        if cls._meta.model:
            return cls
        else:

            class ModuleConfigForm(cls):
                class Meta(cls.Meta):
                    model = self.__class__

            return ModuleConfigForm

    @property
    def key(self):
        return f"module-config-{self.pk}"

    class Meta:
        verbose_name = "Module Config"
        verbose_name_plural = "Module Configs"
        unique_together = ("module", "css_breakpoint")
        ordering = ("css_breakpoint",)
