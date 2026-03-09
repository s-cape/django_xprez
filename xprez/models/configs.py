from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from xprez import constants
from xprez.conf import defaults, settings
from xprez.models.mixins.css import CssMixin, CssParentMixin
from xprez.utils import copy_model, import_class

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

    def duplicate_configs_to(self, target, saved=False):
        for config in self.get_saved_configs():
            existing_config = (
                target.get_configs()
                .filter(css_breakpoint=config.css_breakpoint)
                .first()
            )
            new_config = copy_model(config)
            setattr(new_config, config.parent_attr, target)
            new_config.saved = saved
            if existing_config:
                new_config.pk = existing_config.pk
                new_config._state.adding = False
            new_config.save()

    def _prune_redundant_configs(self):
        """Delete configs identical to their previous breakpoint (after all saves)."""
        configs = list(self.get_saved_configs().order_by("css_breakpoint"))
        for i in range(len(configs) - 1, 0, -1):
            config = configs[i]
            previous_config = configs[i - 1]
            if config._is_redundant_with(previous_config):
                config.delete()


class ConfigBase(CssMixin, models.Model):
    constants = constants

    css_breakpoint = models.PositiveSmallIntegerField(
        choices=BREAKPOINT_CHOICES,
        default=0,
        editable=False,
    )
    saved = models.BooleanField(default=False, editable=False)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.is_default():
            self.saved = True
        super().save(*args, **kwargs)

    def is_default(self):
        return self.css_breakpoint == 0

    def get_admin_form_class(self):
        return import_class(self.form_class)

    def build_admin_form(self, admin, data=None, files=None):
        form_class = self.get_admin_form_class()

        self.admin_form = form_class(
            instance=self, prefix=self.instance_key, data=data, files=files
        )
        self.admin_form.xprez_admin = admin

    def is_admin_form_valid(self):
        if getattr(self.admin_form, "deleted", False):
            return True
        else:
            return self.admin_form.is_valid()

    def save_admin_form(self, request):
        if getattr(self.admin_form, "deleted", False):
            self.delete()
        elif self.admin_form.is_valid():
            inst = self.admin_form.save(commit=False)
            inst.saved = True
            inst.save()

    def render_admin(self, context):
        context["config"] = self
        return render_to_string(self.admin_template_name, context)

    def _is_redundant_with(self, other):
        return all(
            (
                getattr(self, field.name) == getattr(other, field.name)
                or self._is_redundant_exclude(field)
            )
            for field in self._meta.fields
        )

    def _is_redundant_exclude(self, field):
        if field.primary_key:
            return True
        if field.name in {self.parent_attr, "css_breakpoint", "saved"}:
            return True
        remote = getattr(field, "remote_field", None)
        if remote is not None and getattr(remote, "parent_link", False):
            return True
        return False


class SectionConfig(ConfigBase):
    parent_attr = "section"
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
        _("Margin bottom"),
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
        _("Padding right"),
        max_length=20,
        choices=constants.PADDING_CHOICES,
        default=defaults.XPREZ_DEFAULTS["section_config"]["padding_right_choice"],
        blank=True,
    )
    padding_right_custom = models.PositiveIntegerField(null=True, blank=True)
    padding_top_choice = models.CharField(
        _("Padding top"),
        max_length=20,
        choices=constants.PADDING_CHOICES,
        default=defaults.XPREZ_DEFAULTS["section_config"]["padding_top_choice"],
        blank=True,
    )
    padding_top_custom = models.PositiveIntegerField(null=True, blank=True)
    padding_bottom_choice = models.CharField(
        _("Padding bottom"),
        max_length=20,
        choices=constants.PADDING_CHOICES,
        default=defaults.XPREZ_DEFAULTS["section_config"]["padding_bottom_choice"],
        blank=True,
    )
    padding_bottom_custom = models.PositiveIntegerField(null=True, blank=True)

    COLUMN_CHOICES = [(i, str(i)) for i in range(1, 9)]
    columns = models.PositiveSmallIntegerField(
        choices=COLUMN_CHOICES,
        default=defaults.XPREZ_DEFAULTS["section_config"]["columns"],
    )

    gap_choice = models.CharField(
        _("Gap"),
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
    def instance_key(self):
        return f"section-config-{self.pk}"

    class Meta:
        verbose_name = _("Section Config")
        verbose_name_plural = _("Section Configs")
        unique_together = ("section", "css_breakpoint")
        ordering = ("css_breakpoint",)


class ModuleConfig(ConfigBase):
    parent_attr = "module"
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
        _("Column span"),
        default=defaults.XPREZ_DEFAULTS["module_config"]["default"]["colspan"],
    )
    rowspan = models.PositiveSmallIntegerField(
        _("Row span"),
        default=defaults.XPREZ_DEFAULTS["module_config"]["default"]["rowspan"],
    )
    order = models.IntegerField(blank=True, null=True)

    vertical_align_grid = models.CharField(
        _("Vertical align (grid)"),
        max_length=20,
        choices=constants.VERTICAL_ALIGN_GRID_MODULE_CHOICES,
        default=defaults.XPREZ_DEFAULTS["module_config"]["default"][
            "vertical_align_grid"
        ],
    )
    horizontal_align_grid = models.CharField(
        _("Horizontal align (grid)"),
        max_length=20,
        choices=constants.HORIZONTAL_ALIGN_GRID_MODULE_CHOICES,
        default=defaults.XPREZ_DEFAULTS["module_config"]["default"][
            "horizontal_align_grid"
        ],
    )

    vertical_align_flex = models.CharField(
        _("Vertical align (flex)"),
        max_length=20,
        choices=constants.VERTICAL_ALIGN_FLEX_CHOICES,
        default=defaults.XPREZ_DEFAULTS["module_config"]["default"][
            "vertical_align_flex"
        ],
    )
    horizontal_align_flex = models.CharField(
        _("Horizontal align (flex)"),
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
        _("Padding left"),
        max_length=20,
        choices=constants.PADDING_CHOICES,
        default=defaults.XPREZ_DEFAULTS["module_config"]["default"][
            "padding_left_choice"
        ],
        blank=True,
    )
    padding_right_choice = models.CharField(
        _("Padding right"),
        max_length=20,
        choices=constants.PADDING_CHOICES,
        default=defaults.XPREZ_DEFAULTS["module_config"]["default"][
            "padding_right_choice"
        ],
        blank=True,
    )
    padding_top_choice = models.CharField(
        _("Padding top"),
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
        _("Border radius"),
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
        if self.vertical_align_grid != constants.VERTICAL_ALIGN_GRID_UNSET:
            variables["vertical-align-grid"] = self.vertical_align_grid
        if self.horizontal_align_grid != constants.HORIZONTAL_ALIGN_GRID_UNSET:
            variables["horizontal-align-grid"] = self.horizontal_align_grid
        if self.order is not None:
            variables["order"] = self.order
        return variables

    def get_css_config_keys(self):
        return [
            ("module_config", self.module.content_type),
            ("module_config", "default"),
            ("default",),
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
    def instance_key(self):
        return f"module-config-{self.pk}"

    class Meta:
        verbose_name = _("Module Config")
        verbose_name_plural = _("Module Configs")
        unique_together = ("module", "css_breakpoint")
        ordering = ("css_breakpoint",)
