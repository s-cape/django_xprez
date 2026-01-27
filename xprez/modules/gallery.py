from django.db import models
from django.forms import inlineformset_factory

from xprez import constants
from xprez.admin.forms import BaseModuleForm
from xprez.models.configs import ModuleConfig
from xprez.models.modules import Module, MultiModuleItem, UploadMultiModule

PHOTOSWIPE_JS = (
    "xprez/libs/photoswipe/dist/photoswipe.min.js",
    "xprez/libs/photoswipe/dist/photoswipe-ui-default.min.js",
    "xprez/js/photoswipe.js",
)
PHOTOSWIPE_CSS = (
    "xprez/libs/photoswipe/dist/photoswipe.css",
    "xprez/libs/photoswipe/dist/default-skin/default-skin.css",
)


class GalleryModule(UploadMultiModule):
    form_class = "xprez.modules.gallery.GalleryModuleForm"
    admin_template_name = "xprez/admin/modules/gallery/gallery.html"
    admin_formset_item_template_name = "xprez/admin/modules/gallery/gallery_item.html"
    front_template_name = "xprez/modules/gallery.html"
    icon_template_name = "xprez/admin/icons/modules/gallery.html"
    formset_factory = "xprez.modules.gallery.GalleryItemFormSet"
    config_model = "xprez.GalleryConfig"

    # max_width = models.CharField(
    #     max_length=50, choices=Module.SIZE_CHOICES, default=Module.SIZE_FULL
    # )
    crop = models.CharField(
        max_length=5,
        choices=constants.CROP_CHOICES,
        default=constants.CROP_NONE,
        blank=True,
    )

    def save_admin_form(self, request):
        super().save_admin_form(request)
        for index, item in enumerate(self.items.all()):
            item.position = index
            item.save()

    class Meta:
        verbose_name = "Gallery / Image"

    class FrontMedia:
        js = PHOTOSWIPE_JS
        css = PHOTOSWIPE_CSS

    def render_front(self, context):
        if self.items.all().exists():
            return super().render_front(context)
        else:
            return ""


class GalleryItem(MultiModuleItem):
    module = models.ForeignKey(
        GalleryModule, related_name="items", on_delete=models.CASCADE
    )
    file = models.ImageField(upload_to="gallery")
    description = models.CharField(max_length=255, blank=True, null=True)
    alt_text = models.CharField(max_length=255, blank=True)
    position = models.PositiveSmallIntegerField()

    @classmethod
    def create_from_file(cls, django_file, gallery):
        photo = cls(gallery=gallery)
        photo.position = gallery.items.all().count()
        photo.file.save(django_file.name.split("/")[-1], django_file)
        photo.save()
        return photo

    class Meta:
        ordering = ("position",)


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
    columns = models.PositiveSmallIntegerField(choices=COLUMNS_CHOICES, default=1)

    gap_choice = models.CharField(
        "Gap",
        max_length=20,
        choices=constants.GAP_CHOICES,
        default=constants.GAP_SMALL,
        blank=True,
    )
    gap_custom = models.PositiveIntegerField(null=True, blank=True)

    padding_horizontal_choice = models.CharField(
        "Padding horizontal",
        max_length=20,
        choices=constants.PADDING_CHOICES,
        default=constants.PADDING_NONE,
        blank=True,
    )
    padding_horizontal_custom = models.PositiveIntegerField(null=True, blank=True)
    padding_vertical_choice = models.CharField(
        "Padding vertical",
        max_length=20,
        choices=constants.PADDING_CHOICES,
        default=constants.PADDING_NONE,
        blank=True,
    )
    padding_vertical_custom = models.PositiveIntegerField(null=True, blank=True)

    def get_css(self):
        css = super().get_css()
        css.update(
            {
                "columns": self.columns,
                "gap": self._get_choice_or_custom("gap"),
                "padding-horizontal": self._get_choice_or_custom("padding_horizontal"),
                "padding-vertical": self._get_choice_or_custom("padding_vertical"),
            }
        )
        return css


class GalleryModuleForm(BaseModuleForm):
    options_fields = (
        # "width",
        # "columns",
        # "divided",
        "crop",
    ) + BaseModuleForm.options_fields

    class Meta:
        model = GalleryModule
        fields = (
            # "width",
            # "columns",
            # "divided",
            "crop",
        ) + BaseModuleForm.base_module_fields


GalleryItemFormSet = inlineformset_factory(
    GalleryModule,
    GalleryItem,
    fields=("id", "description", "alt_text", "position"),
    extra=0,
    can_delete=True,
)
