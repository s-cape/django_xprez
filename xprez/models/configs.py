from django.db import models
from django.template.loader import render_to_string

from ..conf import settings
from ..utils import import_class

BREAKPOINT_CHOICES = tuple(
    [(k, v["name"]) for k, v in settings.XPREZ_BREAKPOINTS.items()]
)


class ConfigBase(models.Model):
    css_breakpoint = models.PositiveSmallIntegerField(
        choices=BREAKPOINT_CHOICES,
        default=settings.XPREZ_DEFAULT_BREAKPOINT,
        editable=False,
    )

    MARGIN_FULL = "full"
    MARGIN_MEDIUM = "medium"
    MARGIN_SMALL = "small"
    MARGIN_CUSTOM = "custom"
    MARGIN_CHOICES = (
        (MARGIN_FULL, "Full"),
        (MARGIN_MEDIUM, "Medium"),
        (MARGIN_SMALL, "Small"),
        (MARGIN_CUSTOM, "Custom"),
    )

    PADDING_NONE = "none"
    PADDING_SMALL = "small"
    PADDING_MEDIUM = "medium"
    PADDING_LARGE = "large"
    PADDING_CUSTOM = "custom"
    PADDING_CHOICES = (
        (PADDING_NONE, "None"),
        (PADDING_SMALL, "Small"),
        (PADDING_MEDIUM, "Medium"),
        (PADDING_LARGE, "Large"),
        (PADDING_CUSTOM, "Custom"),
    )

    GAP_FULL = "full"
    GAP_MEDIUM = "medium"
    GAP_SMALL = "small"
    GAP_CUSTOM = "custom"
    GAP_CHOICES = (
        (GAP_FULL, "Full"),
        (GAP_MEDIUM, "Medium"),
        (GAP_SMALL, "Small"),
        (GAP_CUSTOM, "Custom"),
    )

    VERTICAL_ALIGN_TOP = "top"
    VERTICAL_ALIGN_MIDDLE = "middle"
    VERTICAL_ALIGN_BOTTOM = "bottom"
    VERTICAL_ALIGN_STRETCH = "stretch"
    VERTICAL_ALIGN_CHOICES = (
        (VERTICAL_ALIGN_TOP, "Top"),
        (VERTICAL_ALIGN_MIDDLE, "Middle"),
        (VERTICAL_ALIGN_BOTTOM, "Bottom"),
        (VERTICAL_ALIGN_STRETCH, "Stretch"),
    )

    HORIZONTAL_ALIGN_LEFT = "left"
    HORIZONTAL_ALIGN_CENTER = "center"
    HORIZONTAL_ALIGN_RIGHT = "right"
    HORIZONTAL_ALIGN_STRETCH = "stretch"
    HORIZONTAL_ALIGN_CHOICES = (
        (HORIZONTAL_ALIGN_LEFT, "Left"),
        (HORIZONTAL_ALIGN_CENTER, "Center"),
        (HORIZONTAL_ALIGN_RIGHT, "Right"),
        (HORIZONTAL_ALIGN_STRETCH, "Stretch"),
    )

    @property
    def css_breakpoint_infix(self):
        return settings.XPREZ_BREAKPOINTS[self.css_breakpoint]["infix"]

    def is_default(self):
        return self.css_breakpoint == settings.XPREZ_DEFAULT_BREAKPOINT

    def get_admin_form_class(self):
        return import_class(self.form_class)

    def build_admin_form(self, admin, data=None, files=None):
        form_class = self.get_admin_form_class()

        self.admin_form = form_class(
            instance=self, prefix=self.get_form_prefix(), data=data, files=files
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
    admin_template_name = "xprez/admin/section_config.html"
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
        choices=ConfigBase.MARGIN_CHOICES,
        default=ConfigBase.MARGIN_MEDIUM,
    )
    margin_bottom_custom = models.PositiveIntegerField(null=True, blank=True)

    padding_left_choice = models.CharField(
        "Padding left",
        max_length=20,
        choices=ConfigBase.PADDING_CHOICES,
        default=ConfigBase.PADDING_NONE,
    )
    padding_right_choice = models.CharField(
        "Padding right",
        max_length=20,
        choices=ConfigBase.PADDING_CHOICES,
        default=ConfigBase.PADDING_NONE,
    )
    padding_top_choice = models.CharField(
        "Padding top",
        max_length=20,
        choices=ConfigBase.PADDING_CHOICES,
        default=ConfigBase.PADDING_NONE,
    )
    padding_bottom_choice = models.CharField(
        "Padding bottom",
        max_length=20,
        choices=ConfigBase.PADDING_CHOICES,
        default=ConfigBase.PADDING_NONE,
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
        choices=ConfigBase.GAP_CHOICES,
        default=ConfigBase.GAP_FULL,
    )
    gap_custom = models.PositiveIntegerField(null=True, blank=True)

    vertical_align = models.CharField(
        max_length=20,
        choices=ConfigBase.VERTICAL_ALIGN_CHOICES,
        default=ConfigBase.VERTICAL_ALIGN_TOP,
    )

    horizontal_align = models.CharField(
        max_length=20,
        choices=ConfigBase.HORIZONTAL_ALIGN_CHOICES,
        default=ConfigBase.HORIZONTAL_ALIGN_LEFT,
    )

    def get_form_prefix(self):
        return "section-config-" + str(self.pk)

    class Meta:
        verbose_name = "Section Config"
        verbose_name_plural = "Section Configs"
        unique_together = ("section", "css_breakpoint")
        ordering = ("css_breakpoint",)


class ContentConfig(ConfigBase):
    """Config for Content/Module models."""

    admin_template_name = "xprez/admin/module_configs/base.html"
    form_class = "xprez.admin.forms.ModuleConfigForm"

    module = models.ForeignKey(
        "xprez.Content",
        on_delete=models.CASCADE,
        related_name="module_configs",
        editable=False,
    )
    visible = models.BooleanField(default=True)

    colspan = models.PositiveSmallIntegerField("Column span", default=1)
    rowspan = models.PositiveSmallIntegerField("Row span", default=1)
    vertical_align = models.CharField(
        max_length=20,
        choices=ConfigBase.VERTICAL_ALIGN_CHOICES,
        default=ConfigBase.VERTICAL_ALIGN_TOP,
    )
    horizontal_align = models.CharField(
        max_length=20,
        choices=ConfigBase.HORIZONTAL_ALIGN_CHOICES,
        default=ConfigBase.HORIZONTAL_ALIGN_LEFT,
    )

    def get_admin_form_class(self):
        cls = super().get_admin_form_class()
        if cls._meta.model:
            return cls
        else:

            class ModuleConfigForm(cls):
                class Meta(cls.Meta):
                    model = self.__class__

            return ModuleConfigForm

    def get_form_prefix(self):
        return "module-config-" + str(self.pk)

    class Meta:
        verbose_name = "Module Config"
        verbose_name_plural = "Module Configs"
        unique_together = ("module", "css_breakpoint")


class TextContentBaseConfig(ContentConfig):
    admin_template_name = "xprez/admin/module_configs/text_base.html"

    border = models.BooleanField(default=True)
    background = models.BooleanField(default=False)


class TextContentConfig(TextContentBaseConfig):
    admin_template_name = "xprez/admin/module_configs/text.html"


# Aliases for new "module" terminology
ModuleConfig = ContentConfig
TextModuleBaseConfig = TextContentBaseConfig
TextModuleConfig = TextContentConfig
