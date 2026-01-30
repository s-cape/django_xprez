from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.template.loader import render_to_string

from xprez import constants
from xprez.conf import defaults, settings
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

    def get_saved_configs(self):
        return self.get_configs().filter(saved=True)

    def get_or_create_config(self, css_breakpoint):
        try:
            return self.get_configs().get(css_breakpoint=css_breakpoint), False
        except ObjectDoesNotExist:
            config = self.build_config(css_breakpoint)
            config.save()
            return config, True


class ConfigBase(CssMixin, models.Model):
    constants = constants

    css_breakpoint = models.PositiveSmallIntegerField(
        choices=BREAKPOINT_CHOICES,
        default=settings.XPREZ_DEFAULT_BREAKPOINT,
        editable=False,
    )
    saved = models.BooleanField(default=False, editable=False)

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

    def save(self, *args, **kwargs):
        if self.is_default():
            self.saved = True
        super().save(*args, **kwargs)

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
        default=defaults.XPREZ_DEFAULTS["section_config"]["margin_bottom_choice"],
        blank=True,
    )
    margin_bottom_custom = models.PositiveIntegerField(
        null=True,
        blank=True,
        default=defaults.XPREZ_DEFAULTS["section_config"]["margin_bottom_custom"],
    )

    padding_left_choice = models.CharField(
        "Padding left",
        max_length=20,
        choices=constants.PADDING_CHOICES,
        default=defaults.XPREZ_DEFAULTS["section_config"]["padding_left_choice"],
        blank=True,
    )
    padding_left_custom = models.PositiveIntegerField(null=True, blank=True)
    padding_right_choice = models.CharField(
        "Padding right",
        max_length=20,
        choices=constants.PADDING_CHOICES,
        default=defaults.XPREZ_DEFAULTS["section_config"]["padding_right_choice"],
        blank=True,
    )
    padding_right_custom = models.PositiveIntegerField(null=True, blank=True)
    padding_top_choice = models.CharField(
        "Padding top",
        max_length=20,
        choices=constants.PADDING_CHOICES,
        default=defaults.XPREZ_DEFAULTS["section_config"]["padding_top_choice"],
        blank=True,
    )
    padding_top_custom = models.PositiveIntegerField(null=True, blank=True)
    padding_bottom_choice = models.CharField(
        "Padding bottom",
        max_length=20,
        choices=constants.PADDING_CHOICES,
        default=defaults.XPREZ_DEFAULTS["section_config"]["padding_bottom_choice"],
        blank=True,
    )
    padding_bottom_custom = models.PositiveIntegerField(null=True, blank=True)

    COLUMN_CHOICES = [(i, str(i)) for i in range(1, 8)]
    columns = models.PositiveSmallIntegerField(
        choices=COLUMN_CHOICES,
        default=defaults.XPREZ_DEFAULTS["section_config"]["columns"],
    )

    gap_choice = models.CharField(
        "Gap",
        max_length=20,
        choices=constants.GAP_CHOICES,
        default=defaults.XPREZ_DEFAULTS["section_config"]["gap_choice"],
        blank=True,
    )
    gap_custom = models.PositiveIntegerField(null=True, blank=True)

    vertical_align_grid = models.CharField(
        max_length=20,
        choices=constants.VERTICAL_ALIGN_GRID_SECTION_CHOICES,
        default=defaults.XPREZ_DEFAULTS["section_config"]["vertical_align_grid"],
    )

    horizontal_align_grid = models.CharField(
        max_length=20,
        choices=constants.HORIZONTAL_ALIGN_GRID_SECTION_CHOICES,
        default=defaults.XPREZ_DEFAULTS["section_config"]["horizontal_align_grid"],
    )

    def get_css_classes(self):
        classes = {}
        if not self.visible:
            classes["invisible"] = not self.visible
        return classes

    def get_css_variables(self):
        return {
            "columns": self.columns,
            "margin-bottom": self._get_choice_or_custom("margin_bottom"),
            "padding": (
                f"{self._get_choice_or_custom('padding_top')} "
                f"{self._get_choice_or_custom('padding_right')} "
                f"{self._get_choice_or_custom('padding_bottom')} "
                f"{self._get_choice_or_custom('padding_left')}"
            ),
            "gap": self._get_choice_or_custom("gap"),
            "vertical-align-grid": self.vertical_align_grid,
            "horizontal-align-grid": self.horizontal_align_grid,
        }

    def get_css_config_keys(self):
        return ("section_config", "default")

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

    colspan = models.PositiveSmallIntegerField(
        "Column span",
        default=defaults.XPREZ_DEFAULTS["module_config"]["default"]["colspan"],
    )
    rowspan = models.PositiveSmallIntegerField(
        "Row span",
        default=defaults.XPREZ_DEFAULTS["module_config"]["default"]["rowspan"],
    )

    vertical_align_grid = models.CharField(
        "Vertical align (grid)",
        max_length=20,
        choices=constants.VERTICAL_ALIGN_GRID_MODULE_CHOICES,
        default=defaults.XPREZ_DEFAULTS["module_config"]["default"][
            "vertical_align_grid"
        ],
    )
    horizontal_align_grid = models.CharField(
        "Horizontal align (grid)",
        max_length=20,
        choices=constants.HORIZONTAL_ALIGN_GRID_MODULE_CHOICES,
        default=defaults.XPREZ_DEFAULTS["module_config"]["default"][
            "horizontal_align_grid"
        ],
    )

    vertical_align_flex = models.CharField(
        "Vertical align (flex)",
        max_length=20,
        choices=constants.VERTICAL_ALIGN_FLEX_CHOICES,
        default=defaults.XPREZ_DEFAULTS["module_config"]["default"][
            "vertical_align_flex"
        ],
    )
    horizontal_align_flex = models.CharField(
        "Horizontal align (flex)",
        max_length=20,
        choices=constants.HORIZONTAL_ALIGN_FLEX_CHOICES,
        default=defaults.XPREZ_DEFAULTS["module_config"]["default"][
            "horizontal_align_flex"
        ],
    )

    background = models.BooleanField(
        default=defaults.XPREZ_DEFAULTS["module_config"]["default"]["background"]
    )
    border = models.BooleanField(
        default=defaults.XPREZ_DEFAULTS["module_config"]["default"]["border"]
    )
    background_color = models.CharField(
        max_length=30,
        blank=True,
        default=defaults.XPREZ_DEFAULTS["module_config"]["default"]["background_color"],
    )

    padding_left_choice = models.CharField(
        "Padding left",
        max_length=20,
        choices=constants.PADDING_CHOICES,
        default=defaults.XPREZ_DEFAULTS["module_config"]["default"][
            "padding_left_choice"
        ],
        blank=True,
    )
    padding_right_choice = models.CharField(
        "Padding right",
        max_length=20,
        choices=constants.PADDING_CHOICES,
        default=defaults.XPREZ_DEFAULTS["module_config"]["default"][
            "padding_right_choice"
        ],
        blank=True,
    )
    padding_top_choice = models.CharField(
        "Padding top",
        max_length=20,
        choices=constants.PADDING_CHOICES,
        default=defaults.XPREZ_DEFAULTS["module_config"]["default"][
            "padding_top_choice"
        ],
        blank=True,
    )
    padding_bottom_choice = models.CharField(
        "Padding bottom",
        max_length=20,
        choices=constants.PADDING_CHOICES,
        default=defaults.XPREZ_DEFAULTS["module_config"]["default"][
            "padding_bottom_choice"
        ],
        blank=True,
    )
    padding_left_custom = models.PositiveIntegerField(
        null=True,
        blank=True,
        default=defaults.XPREZ_DEFAULTS["module_config"]["default"][
            "padding_left_custom"
        ],
    )
    padding_right_custom = models.PositiveIntegerField(
        null=True,
        blank=True,
        default=defaults.XPREZ_DEFAULTS["module_config"]["default"][
            "padding_right_custom"
        ],
    )
    padding_top_custom = models.PositiveIntegerField(
        null=True,
        blank=True,
        default=defaults.XPREZ_DEFAULTS["module_config"]["default"][
            "padding_top_custom"
        ],
    )
    padding_bottom_custom = models.PositiveIntegerField(
        null=True,
        blank=True,
        default=defaults.XPREZ_DEFAULTS["module_config"]["default"][
            "padding_bottom_custom"
        ],
    )
    aspect_ratio = models.CharField(
        max_length=20,
        blank=True,
        default=defaults.XPREZ_DEFAULTS["module_config"]["default"]["aspect_ratio"],
    )
    border_radius_choice = models.CharField(
        "Border radius",
        max_length=20,
        choices=constants.BORDER_RADIUS_CHOICES,
        default=defaults.XPREZ_DEFAULTS["module_config"]["default"][
            "border_radius_choice"
        ],
        blank=True,
    )
    border_radius_custom = models.PositiveIntegerField(
        null=True,
        blank=True,
        default=defaults.XPREZ_DEFAULTS["module_config"]["default"][
            "border_radius_custom"
        ],
    )

    def get_css_classes(self):
        classes = {}
        if not self.visible:
            classes["invisible"] = not self.visible
        if self.background:
            classes["background"] = True
        if self.border:
            classes["border"] = True
        return classes

    def get_css_variables(self):
        variables = {
            "colspan": self.colspan,
            "rowspan": self.rowspan,
            "vertical-align-grid": self.vertical_align_grid,
            "horizontal-align-grid": self.horizontal_align_grid,
            "vertical-align-flex": self.vertical_align_flex,
            "horizontal-align-flex": self.horizontal_align_flex,
            "padding": (
                f"{self._get_choice_or_custom('padding_top')} "
                f"{self._get_choice_or_custom('padding_right')} "
                f"{self._get_choice_or_custom('padding_bottom')} "
                f"{self._get_choice_or_custom('padding_left')}"
            ),
            "aspect-ratio": self.aspect_ratio if self.aspect_ratio else "none",
            "border-radius": self._get_choice_or_custom("border_radius"),
        }
        if self.background and self.background_color:
            variables["background-color"] = self.background_color
        return variables

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
