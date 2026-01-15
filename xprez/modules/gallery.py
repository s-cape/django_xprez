from django.db import models
from django.forms import inlineformset_factory

from xprez.admin.forms import BaseModuleForm
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
    COLUMNS_CHOICES = (
        (1, "1"),
        (2, "2"),
        (3, "3"),
        (4, "4"),
        (6, "6"),
        (8, "8"),
    )

    form_class = "xprez.modules.gallery.GalleryModuleForm"
    admin_template_name = "xprez/admin/modules/gallery/gallery.html"
    admin_formset_item_template_name = "xprez/admin/modules/gallery/gallery_item.html"
    front_template_name = "xprez/modules/gallery.html"
    icon_template_name = "xprez/admin/icons/modules/gallery.html"
    formset_factory = "xprez.modules.gallery.GalleryItemFormSet"

    width = models.CharField(
        max_length=50, choices=Module.SIZE_CHOICES, default=Module.SIZE_FULL
    )
    columns = models.PositiveSmallIntegerField(default=1)
    divided = models.BooleanField(default=False)
    crop = models.BooleanField(default=False)

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


class GalleryModuleForm(BaseModuleForm):
    options_fields = (
        "width",
        "columns",
        "divided",
        "crop",
    ) + BaseModuleForm.options_fields

    class Meta:
        model = GalleryModule
        fields = (
            "width",
            "columns",
            "divided",
            "crop",
        ) + BaseModuleForm.base_module_fields


GalleryItemFormSet = inlineformset_factory(
    GalleryModule,
    GalleryItem,
    fields=("id", "description", "alt_text", "position"),
    extra=0,
    can_delete=True,
)
