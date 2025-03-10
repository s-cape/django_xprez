from django.db import models

from ..conf import settings

BREAKPOINT_CHOICES = tuple(
    [(k, v["name"]) for k, v in settings.XPREZ_BREAKPOINTS.items()]
)

MARGIN_FULL = "full"
MARGIN_MEDIUM = "medium"
MARGIN_SMALL = "small"
MARGIN_CUSTOM = "custom"
MARGIN_CHOICES = (
    (MARGIN_FULL, "full"),
    (MARGIN_MEDIUM, "medium"),
    (MARGIN_SMALL, "small"),
    (MARGIN_CUSTOM, "custom"),
)

PADDING_NONE = "none"
PADDING_SMALL = "small"
PADDING_MEDIUM = "medium"
PADDING_LARGE = "large"
PADDING_CUSTOM = "custom"
PADDING_CHOICES = (
    (PADDING_NONE, "none"),
    (PADDING_SMALL, "small"),
    (PADDING_MEDIUM, "medium"),
    (PADDING_LARGE, "large"),
    (PADDING_CUSTOM, "custom"),
)


class SectionConfig(models.Model):
    section = models.ForeignKey(
        "xprez.Section", on_delete=models.CASCADE, related_name="configs"
    )
    css_breakpoint = models.PositiveSmallIntegerField(
        choices=BREAKPOINT_CHOICES, default=settings.XPREZ_DEFAULT_BREAKPOINT
    )
    saved = models.BooleanField(default=False)
    visible = models.BooleanField(default=True)

    margin_bottom_choice = models.CharField(
        max_length=20, choices=MARGIN_CHOICES, default=MARGIN_MEDIUM
    )
    margin_bottom_custom = models.PositiveIntegerField(null=True, blank=True)

    padding_left_choice = models.CharField(
        max_length=20, choices=PADDING_CHOICES, default=PADDING_NONE
    )
    padding_right_choice = models.CharField(
        max_length=20, choices=PADDING_CHOICES, default=PADDING_NONE
    )
    padding_top_choice = models.CharField(
        max_length=20, choices=PADDING_CHOICES, default=PADDING_NONE
    )
    padding_bottom_choice = models.CharField(
        max_length=20, choices=PADDING_CHOICES, default=PADDING_NONE
    )
    padding_left_custom = models.PositiveIntegerField(null=True, blank=True)
    padding_right_custom = models.PositiveIntegerField(null=True, blank=True)
    padding_top_custom = models.PositiveIntegerField(null=True, blank=True)
    padding_bottom_custom = models.PositiveIntegerField(null=True, blank=True)
    padding_x_linked = models.BooleanField(default=True)
    padding_y_linked = models.BooleanField(default=True)

    COLUMN_CHOICES = [(i, str(i)) for i in range(1, 8)]
    columns = models.PositiveSmallIntegerField(choices=COLUMN_CHOICES, default=1)

    GAP_FULL = "full"
    GAP_MEDIUM = "medium"
    GAP_SMALL = "small"
    GAP_CUSTOM = "custom"
    GAP_CHOICES = (
        (GAP_FULL, "full"),
        (GAP_MEDIUM, "medium"),
        (GAP_SMALL, "small"),
        (GAP_CUSTOM, "custom"),
    )
    gap_choice = models.CharField(max_length=20, choices=GAP_CHOICES, default=GAP_FULL)
    gap_custom = models.PositiveIntegerField(null=True, blank=True)

    VERTICAL_ALIGN_TOP = "top"
    VERTICAL_ALIGN_MIDDLE = "middle"
    VERTICAL_ALIGN_BOTTOM = "bottom"
    VERTICAL_ALIGN_STRETCH = "stretch"
    VERTICAL_ALIGN_CHOICES = (
        (VERTICAL_ALIGN_TOP, "top"),
        (VERTICAL_ALIGN_MIDDLE, "middle"),
        (VERTICAL_ALIGN_BOTTOM, "bottom"),
        (VERTICAL_ALIGN_STRETCH, "stretch"),
    )
    vertical_align = models.CharField(
        max_length=20, choices=VERTICAL_ALIGN_CHOICES, default=VERTICAL_ALIGN_TOP
    )

    HORIZONTAL_ALIGN_LEFT = "left"
    HORIZONTAL_ALIGN_CENTER = "center"
    HORIZONTAL_ALIGN_RIGHT = "right"
    HORIZONTAL_ALIGN_STRETCH = "stretch"
    HORIZONTAL_ALIGN_CHOICES = (
        (HORIZONTAL_ALIGN_LEFT, "left"),
        (HORIZONTAL_ALIGN_CENTER, "center"),
        (HORIZONTAL_ALIGN_RIGHT, "right"),
        (HORIZONTAL_ALIGN_STRETCH, "stretch"),
    )
    horizontal_align = models.CharField(
        max_length=20, choices=HORIZONTAL_ALIGN_CHOICES, default=HORIZONTAL_ALIGN_LEFT
    )

    @property
    def css_breakpoint_infix(self):
        return settings.XPREZ_BREAKPOINTS[self.css_breakpoint]["infix"]

    class Meta:
        verbose_name = "Section Config"
        verbose_name_plural = "Section Configs"
        unique_together = ("section", "css_breakpoint")
        ordering = ("css_breakpoint",)


class ContentConfig(models.Model):
    content = models.ForeignKey(
        "xprez.Content", on_delete=models.CASCADE, related_name="configs"
    )
    css_breakpoint = models.PositiveSmallIntegerField(
        choices=BREAKPOINT_CHOICES,
        default=settings.XPREZ_DEFAULT_BREAKPOINT,
    )
    visible = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Content Config"
        verbose_name_plural = "Content Configs"
        unique_together = ("content", "css_breakpoint")
