from django.db import models
from django.utils.functional import cached_property

from xprez import constants
from xprez.admin.forms import ModuleForm, MultiModuleItemForm
from xprez.conf import defaults, settings
from xprez.models.configs import ModuleConfig
from xprez.models.modules import FontSizeModuleMixin, MultiModuleItem, UploadMultiModule

PHOTOSWIPE_JS = (
    "xprez/libs/photoswipe/dist/photoswipe.min.js",
    "xprez/libs/photoswipe/dist/photoswipe-ui-default.min.js",
    "xprez/js/photoswipe.js",
)
PHOTOSWIPE_CSS = (
    "xprez/libs/photoswipe/dist/photoswipe.css",
    "xprez/libs/photoswipe/dist/default-skin/default-skin.css",
)


class GalleryModule(FontSizeModuleMixin, UploadMultiModule):
    config_model = "xprez.GalleryConfig"
    front_template_name = "xprez/modules/gallery.html"
    admin_template_name = "xprez/admin/modules/gallery/gallery.html"
    admin_item_template_name = "xprez/admin/modules/gallery/gallery_item.html"
    admin_form_class = "xprez.modules.gallery.GalleryModuleForm"
    admin_item_form_class = "xprez.modules.gallery.GalleryItemForm"
    admin_icon_template_name = "xprez/admin/icons/modules/gallery.html"

    crop = models.CharField(
        max_length=5,
        choices=constants.CROP_CHOICES,
        default=defaults.XPREZ_DEFAULTS["module"]["xprez.GalleryModule"]["crop"],
        blank=True,
    )

    class Meta:
        verbose_name = "Gallery / Image"

    class FrontMedia:
        js = PHOTOSWIPE_JS
        css = PHOTOSWIPE_CSS

    def render_front(self, context):
        if self.items.all().exists():
            return super().render_front(context)
        return ""

    @property
    def thumbnail_crop(self):
        """Sorl crop option: 'center' when aspect crop set, else no crop."""
        return "center" if self.crop else ""

    def get_crop_ratio(self):
        """Return (numerator, denominator) from self.crop (e.g. '3/4'), or None."""
        if not self.crop or "/" not in self.crop:
            return None
        else:
            num, den = self.crop.split("/", 1)
            return (int(num.strip()), int(den.strip()))

    def get_section_max_width_px(self):
        """Section max-width in px, or None for full-width."""
        width_choice = self.section.max_width_choice
        if width_choice == constants.MAX_WIDTH_FULL:
            return None
        elif width_choice == constants.MAX_WIDTH_CUSTOM:
            return self.section.max_width_custom or None
        else:
            max_width_values = settings.XPREZ_CSS["section"]["max_width"]["values"]
            return max_width_values.get(width_choice, {}).get(0)

    @cached_property
    def get_image_sizes(self):
        """Build HTML sizes attribute string for responsive gallery images."""
        max_width, ranges = self._compute_column_ranges()
        entries = []
        for index, (min_width, effective_columns) in enumerate(ranges):
            if index + 1 < len(ranges):
                next_min_width = ranges[index + 1][0]
            else:
                next_min_width = None
            vw_size = f"{self._format_percentage(100 / effective_columns)}vw"
            if max_width is None:
                entries += [self._media_entry(vw_size, next_min_width)]
            elif min_width >= max_width:
                px_size = round(max_width / effective_columns)
                entries += [self._media_entry(f"{px_size}px", next_min_width)]
            elif next_min_width is None or next_min_width > max_width:
                entries += [self._media_entry(vw_size, max_width)]
                px_size = round(max_width / effective_columns)
                entries += [self._media_entry(f"{px_size}px", next_min_width)]
            else:
                entries += [self._media_entry(vw_size, next_min_width)]
        return ", ".join(entries)

    @cached_property
    def get_srcset_widths(self):
        """Candidate widths for srcset, capped at full_width_cap."""
        max_width = self.get_section_max_width_px()
        full_width_cap = settings.XPREZ_GALLERY_FULL_WIDTH_PX
        if max_width is None:
            max_boundary = full_width_cap
        else:
            max_boundary = min(max_width, full_width_cap)
        candidate_widths = set()
        for (
            _,
            effective_columns,
            next_min_width,
        ) in self._iter_breakpoint_columns():
            if max_width is None:
                boundary = min(next_min_width or full_width_cap, full_width_cap)
                pixel_width = round(boundary / effective_columns)
                candidate_widths.add(pixel_width)
                candidate_widths.add(pixel_width * 2)
            elif next_min_width is not None and next_min_width <= max_boundary:
                pixel_width = round(next_min_width / effective_columns)
                candidate_widths.add(pixel_width)
                candidate_widths.add(pixel_width * 2)
            if max_width is not None and (
                next_min_width is None or next_min_width > max_width
            ):
                pixel_width = round(max_boundary / effective_columns)
                candidate_widths.add(pixel_width)
                candidate_widths.add(pixel_width * 2)
        retina_cap = full_width_cap * 2
        return sorted(width for width in candidate_widths if 0 < width <= retina_cap)

    # -- Private helpers --

    @staticmethod
    def _format_percentage(value):
        rounded = round(value, 2)
        return int(rounded) if rounded == int(rounded) else rounded

    @staticmethod
    def _media_entry(value, breakpoint=None):
        """Wrap value in a CSS media query if breakpoint is given."""
        if breakpoint:
            return f"(max-width: {breakpoint}px) {value}"
        return value

    def _iter_breakpoint_columns(self):
        """Yield (min_width, effective_columns, next_min_width) per breakpoint."""
        breakpoints = settings.XPREZ_BREAKPOINTS
        section_configs = {
            config.css_breakpoint: config for config in self.section.get_saved_configs()
        }
        gallery_configs = {
            config.css_breakpoint: config for config in self.get_saved_configs()
        }
        current_section_cols = 1
        current_gallery_cols = 1
        current_colspan = 1
        bp_ids = list(breakpoints)
        for index, bp_id in enumerate(bp_ids):
            if bp_id in section_configs:
                current_section_cols = section_configs[bp_id].columns
            if bp_id in gallery_configs:
                current_gallery_cols = gallery_configs[bp_id].columns
                current_colspan = gallery_configs[bp_id].colspan
            effective_columns = max(
                1,
                current_section_cols * current_gallery_cols // current_colspan,
            )
            min_width = breakpoints[bp_id]["min_width"]
            if index + 1 < len(bp_ids):
                next_bp_id = bp_ids[index + 1]
                next_min_width = breakpoints[next_bp_id]["min_width"]
            else:
                next_min_width = None
            yield min_width, effective_columns, next_min_width

    def _compute_column_ranges(self):
        """Return (max_width_px, ranges) with consecutive duplicate columns removed."""
        max_width = self.get_section_max_width_px()
        ranges = []
        for min_width, effective_columns, _ in self._iter_breakpoint_columns():
            if not ranges or ranges[-1][1] != effective_columns:
                ranges += [(min_width, effective_columns)]
        return max_width, ranges


class GalleryItem(MultiModuleItem):
    module = models.ForeignKey(
        GalleryModule, related_name="items", on_delete=models.CASCADE
    )
    file = models.ImageField(upload_to="gallery")
    description = models.CharField(max_length=255, blank=True, null=True)
    alt_text = models.CharField(max_length=255, blank=True)

    @cached_property
    def get_srcset_geometries(self):
        """Srcset geometry strings capped at this item's image width (no upscale)."""
        try:
            max_image_width = self.file.width
        except Exception:
            max_image_width = settings.XPREZ_GALLERY_FULL_WIDTH_PX
        if not max_image_width:
            max_image_width = settings.XPREZ_GALLERY_FULL_WIDTH_PX
        capped_widths = [
            width for width in self.module.get_srcset_widths if width <= max_image_width
        ]
        if not capped_widths:
            capped_widths = [max_image_width]
        crop_ratio = self.module.get_crop_ratio()
        if crop_ratio:
            numerator, denominator = crop_ratio
            return [
                f"{width}x{round(width * denominator / numerator)}"
                for width in capped_widths
            ]
        return [f"{width}x{width}" for width in capped_widths]

    @classmethod
    def create_from_file(cls, django_file, gallery):
        item = cls(module=gallery, position=gallery.items.count())
        item.file.save(django_file.name.split("/")[-1], django_file)
        item.save()
        return item


class GalleryConfig(ModuleConfig):
    admin_template_name = "xprez/admin/configs/modules/gallery.html"

    COLUMNS_CHOICES = (
        (1, "1"),
        (2, "2"),
        (3, "3"),
        (4, "4"),
        (6, "6"),
        (8, "8"),
    )
    columns = models.PositiveSmallIntegerField(
        choices=COLUMNS_CHOICES,
        default=defaults.XPREZ_DEFAULTS["module_config"]["xprez.GalleryModule"][
            "columns"
        ],
    )

    gap_choice = models.CharField(
        "Gap",
        max_length=20,
        choices=constants.GAP_CHOICES,
        default=defaults.XPREZ_DEFAULTS["module_config"]["xprez.GalleryModule"][
            "gap_choice"
        ],
        blank=True,
    )
    gap_custom = models.PositiveIntegerField(null=True, blank=True)

    def get_css_variables(self):
        css_variables = super().get_css_variables()
        css_variables.update(
            {
                "columns": self.columns,
                "gap": self._get_choice_or_custom("gap"),
            }
        )
        return css_variables


class GalleryModuleForm(ModuleForm):
    options_fields = ModuleForm.options_fields + (
        "font_size",
        "crop",
    )

    class Meta:
        model = GalleryModule
        fields = "__all__"


class GalleryItemForm(MultiModuleItemForm):
    class Meta:
        model = GalleryItem
        fields = ("description", "alt_text")
