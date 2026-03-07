from django.db import models

from xprez import constants
from xprez.admin.forms import ModuleForm, MultiModuleItemForm
from xprez.conf import defaults, settings
from xprez.models.configs import ModuleConfig
from xprez.models.mixins.font_size import FontSizeModuleMixin
from xprez.models.mixins.responsive_image import (
    ResponsiveImageItemMixin,
    ResponsiveImageParentMixin,
)
from xprez.models.multi_module import MultiModuleItem, UploadMultiModule

PHOTOSWIPE_JS = (
    "xprez/libs/photoswipe/dist/photoswipe.min.js",
    "xprez/libs/photoswipe/dist/photoswipe-ui-default.min.js",
    "xprez/js/photoswipe.js",
)
PHOTOSWIPE_CSS = (
    "xprez/libs/photoswipe/dist/photoswipe.css",
    "xprez/libs/photoswipe/dist/default-skin/default-skin.css",
)


class GalleryModule(FontSizeModuleMixin, ResponsiveImageParentMixin, UploadMultiModule):
    config_model = "xprez.GalleryConfig"
    front_template_name = "xprez/modules/gallery.html"
    admin_template_name = "xprez/admin/modules/gallery/gallery.html"
    admin_item_template_name = "xprez/admin/modules/gallery/gallery_item.html"
    admin_form_class = "xprez.modules.gallery.GalleryModuleForm"
    admin_item_form_class = "xprez.modules.gallery.GalleryItemForm"
    admin_icon_template_name = "xprez/shared/icons/modules/gallery.html"

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
        css = {"all": PHOTOSWIPE_CSS}

    def get_crop_ratio(self):
        """Return (numerator, denominator) from self.crop (e.g. '3/4'), or None."""
        return self.parse_crop_string(self.crop)

    @property
    def thumbnail_crop(self):
        if self.get_crop_ratio():
            return "center"
        else:
            return ""

    def get_breakpoint_ranges(self):
        result = []
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
        for bp_id in breakpoints:
            if bp_id in section_configs:
                current_section_cols = section_configs[bp_id].columns
            if bp_id in gallery_configs:
                current_gallery_cols = gallery_configs[bp_id].columns
                current_colspan = gallery_configs[bp_id].colspan
            effective_columns = max(
                1,
                current_section_cols * current_gallery_cols // current_colspan,
            )
            result += [(breakpoints[bp_id]["max_width"], effective_columns)]
        return result


class GalleryItem(ResponsiveImageItemMixin, MultiModuleItem):
    module = models.ForeignKey(
        GalleryModule, related_name="items", on_delete=models.CASCADE
    )
    file = models.ImageField(upload_to="gallery")
    description = models.CharField(max_length=255, blank=True, null=True)
    alt_text = models.CharField(max_length=255, blank=True)

    def get_image_field(self):
        return self.file

    def get_aspect_ratio(self):
        crop_ratio = self.module.get_crop_ratio()
        return crop_ratio if crop_ratio else (1, 1)

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
        fields = "__all__"
