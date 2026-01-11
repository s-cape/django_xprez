# -*- coding: utf-8 -*-
from os import makedirs, path

from django.conf import settings as django_settings
from django.db import models
from django.http import JsonResponse
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.urls import re_path
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from xprez.admin.fields import TemplatePathField
from xprez.admin.permissions import xprez_staff_member_required
from xprez.ck_editor import parse_text as ckeditor_parse_text
from xprez.ck_editor.widgets import CkEditorWidget
from xprez.conf import settings
from xprez.models.base import (
    CLIPBOARD_TEXT_MAX_LENGTH,
    Module,
    MultiModule,
    MultiModuleItem,
    UploadMultiModule,
)
from xprez.utils import random_string, truncate_with_ellipsis

PHOTOSWIPE_JS = (
    "xprez/libs/photoswipe/dist/photoswipe.min.js",
    "xprez/libs/photoswipe/dist/photoswipe-ui-default.min.js",
    "xprez/js/photoswipe.js",
)
PHOTOSWIPE_CSS = (
    "xprez/libs/photoswipe/dist/photoswipe.css",
    "xprez/libs/photoswipe/dist/default-skin/default-skin.css",
)


class CkEditorFileUploadMixin:
    @classmethod
    @method_decorator(xprez_staff_member_required)
    @method_decorator(csrf_exempt)
    def file_upload_view(cls, request, directory):
        if request.method == "POST":
            file_data = request.FILES["upload"]
            name = file_data.name
            random_dir_name = random_string(16)
            full_directory = path.join(
                django_settings.MEDIA_ROOT, directory, random_dir_name
            )
            if not path.isdir(full_directory):
                makedirs(full_directory)

            with open(path.join(full_directory, name), "wb+") as destination:
                for chunk in file_data.chunks():
                    destination.write(chunk)

            filename = path.join(directory, random_dir_name, name)

            return JsonResponse({"url": django_settings.MEDIA_URL + filename})

    @classmethod
    def get_urls(cls):
        cls_name = cls.__name__.lower()
        return [
            re_path(
                r"^{}/file-upload/(?P<directory>[/\w-]+)/$".format(cls_name),
                cls.file_upload_view,
                name="{}_file_upload".format(cls_name),
            ),
        ]


class TextModuleBase(CkEditorFileUploadMixin, Module):
    form_class = "xprez.admin.forms.TextModuleBaseForm"
    admin_template_name = "xprez/admin/modules/text_base.html"
    front_template_name = "xprez/modules/text_base.html"
    icon_template_name = "xprez/admin/icons/modules/text_base.html"
    config_model = "xprez.TextModulBaseConfig"

    text = models.TextField(blank=True)

    class Meta:
        abstract = True


class TextModule(TextModuleBase):
    form_class = "xprez.admin.forms.TextModuleForm"
    admin_template_name = "xprez/admin/modules/text.html"
    front_template_name = "xprez/modules/text.html"
    icon_template_name = "xprez/admin/icons/modules/text.html"
    config_model = "xprez.TextModuleConfig"

    image = models.ImageField(upload_to="images", null=True, blank=True)
    url = models.CharField("Target URL", max_length=255, null=True, blank=True)

    class AdminMedia:
        js = CkEditorWidget.Media.js
        css = {"css": CkEditorWidget.Media.css["all"]}

    class Meta:
        verbose_name = "Text"

    def render_front(self, context):
        context["parsed_text"] = ckeditor_parse_text.render_text_parsed(
            ckeditor_parse_text.parse_text(self.text, context["request"])
        )
        return super().render_front(context)

    def clipboard_text_preview(self):
        return truncate_with_ellipsis(self.text, CLIPBOARD_TEXT_MAX_LENGTH)


class QuoteModule(Module):
    # form_class = "xprez.admin.forms.QuotesModuleForm"
    # formset_factory = "xprez.admin.forms.QuotesItemFormSet"
    admin_template_name = "xprez/admin/modules/quote.html"
    front_template_name = "xprez/modules/quote.html"
    icon_template_name = "xprez/admin/icons/modules/quote.html"

    name = models.CharField(max_length=255)
    job_title = models.CharField(max_length=255)
    image = models.ImageField(upload_to="quotes", null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    quote = models.TextField()

    class Meta:
        verbose_name = "Quote"

    # title = models.CharField(max_length=255, null=True, blank=True)
    # box = models.BooleanField(default=False)

    # display_two = models.BooleanField(default=False)

    # def get_formset_queryset(self):
    #     return self.quotes.all()

    # def show_front(self):
    #     quotes = self.quotes.all()
    #     if len(quotes) == 0:
    #         return False
    #     quote = quotes.first()
    #     if not quote.name or not quote.quote:
    #         return False
    #     return True


# class QuotesItem(ModuleItem):
#     module = models.ForeignKey(
#         QuotesModule, related_name="quotes", on_delete=models.CASCADE
#     )
#     name = models.CharField(max_length=255)
#     job_title = models.CharField(max_length=255)
#     image = models.ImageField(upload_to="quotes", null=True, blank=True)
#     title = models.CharField(max_length=255, null=True, blank=True)
#     quote = models.TextField()

#     class Meta:
#         ordering = ("module", "id")


class GalleryModule(UploadMultiModule):
    COLUMNS_CHOICES = (
        (1, "1"),
        (2, "2"),
        (3, "3"),
        (4, "4"),
        (6, "6"),
        (8, "8"),
    )

    form_class = "xprez.admin.forms.GalleryModuleForm"
    admin_template_name = "xprez/admin/modules/gallery/gallery.html"
    admin_formset_item_template_name = "xprez/admin/modules/gallery/gallery_item.html"
    front_template_name = "xprez/modules/gallery.html"
    icon_template_name = "xprez/admin/icons/modules/gallery.html"
    formset_factory = "xprez.admin.forms.GalleryItemFormSet"

    width = models.CharField(
        max_length=50, choices=Module.SIZE_CHOICES, default=Module.SIZE_FULL
    )
    columns = models.PositiveSmallIntegerField(default=1)
    divided = models.BooleanField(default=False)
    crop = models.BooleanField(default=False)

    def get_formset_queryset(self):
        return self.items.all()

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

    def show_front(self):
        return self.photos.all().count()


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


class VideoModule(Module):
    TYPE_CHOICES = (
        ("youtube", "YouTube"),
        ("vimeo", "Vimeo"),
    )
    admin_template_name = "xprez/admin/modules/video.html"
    front_template_name = "xprez/modules/video.html"
    icon_template_name = "xprez/admin/icons/modules/video.html"
    form_class = "xprez.admin.forms.VideoForm"

    poster_image = models.ImageField(upload_to="video", null=True, blank=True)
    url = models.URLField()
    width = models.CharField(
        max_length=50, choices=Module.SIZE_CHOICES, default=Module.SIZE_FULL
    )
    video_type = models.CharField(choices=TYPE_CHOICES, max_length=50)
    video_id = models.CharField(max_length=200)

    def save_admin_form(self, request):
        inst = self.admin_form.save(commit=False)
        inst.video_type = self.admin_form.video_type
        inst.video_id = self.admin_form.video_id
        inst.save()

    def show_front(self):
        return self.url

    class FrontMedia:
        js = (
            "xprez/js/video.js",
            "//www.youtube.com/iframe_api",
            "//player.vimeo.com/api/player.js",
        )


class CodeInputModule(Module):
    admin_template_name = "xprez/admin/modules/code_input.html"
    front_template_name = "xprez/modules/code_input.html"
    icon_template_name = "xprez/admin/icons/modules/code_input.html"
    form_class = "xprez.admin.forms.CodeInputModuleForm"

    code = models.TextField()

    def show_front(self):
        return self.code


class NumbersModule(MultiModule):
    admin_template_name = "xprez/admin/modules/numbers.html"
    front_template_name = "xprez/modules/numbers.html"
    icon_template_name = "xprez/admin/icons/modules/numbers.html"
    form_class = "xprez.admin.forms.NumbersModuleForm"
    formset_factory = "xprez.admin.forms.NumberFormSet"

    def get_formset_queryset(self):
        return self.numbers.all()

    def show_front(self):
        return self.numbers.all().count()

    class Meta:
        verbose_name = "Numbers"

    class FrontMedia:
        js = (
            "xprez/libs/jquery.waypoints.min.js",
            "xprez/libs/counter.up/jquery.counterup.js",
            "xprez/js/numbers.js",
        )


class NumbersItem(MultiModuleItem):
    module = models.ForeignKey(
        NumbersModule, related_name="items", on_delete=models.CASCADE
    )
    number = models.IntegerField(null=True, blank=True)
    suffix = models.CharField(max_length=10, null=True, blank=True)
    title = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ("module", "id")


class CodeTemplateModule(Module):
    admin_template_name = "xprez/admin/modules/code_template.html"
    icon_template_name = "xprez/admin/icons/modules/code_template.html"
    form_class = "xprez.admin.forms.CodeTemplateModuleForm"

    @staticmethod
    def get_template_dir():
        if settings.XPREZ_CODE_TEMPLATES_DIR:
            return settings.XPREZ_CODE_TEMPLATES_DIR

        # Try TEMPLATES DIRS as fallback
        for engine in settings.TEMPLATES:
            if engine.get("DIRS"):
                return engine["DIRS"][0]

        return ""

    template_name = TemplatePathField(
        template_dir=get_template_dir(),
        prefix=settings.XPREZ_CODE_TEMPLATES_PREFIX,
        match=r"^(?!\.).+",
        max_length=255,
        null=True,
        blank=True,
    )

    def render_front(self, context):
        if self.template_name:
            context["module"] = self
            try:
                return get_template(self.template_name).render(context=context)
            except TemplateDoesNotExist:
                return "Invalid Template"
        else:
            return ""


class DownloadsModule(UploadMultiModule):
    admin_template_name = "xprez/admin/modules/downloads/downloads.html"
    front_template_name = "xprez/modules/downloads.html"
    admin_formset_item_template_name = (
        "xprez/admin/modules/downloads/downloads_item.html"
    )
    icon_template_name = "xprez/admin/icons/modules/downloads.html"
    form_class = "xprez.admin.forms.DownloadModuleForm"
    formset_factory = "xprez.admin.forms.AttachmentFormSet"

    title = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Files"

    def get_formset_queryset(self):
        return self.attachments.all()

    def show_front(self):
        return self.attachments.all().count()


class DownloadsItem(MultiModuleItem):
    module = models.ForeignKey(
        DownloadsModule, related_name="items", on_delete=models.CASCADE
    )
    file = models.FileField(upload_to="files", max_length=300)
    name = models.CharField(max_length=100, blank=True)
    position = models.PositiveSmallIntegerField()

    def get_name(self):
        return self.name or self.get_default_file_name()

    def get_extension(self):
        try:
            return self.file.name.split("/")[-1].split(".")[-1].lower()
        except (KeyError, IndexError):
            return ""

    def get_default_file_name(self):
        try:
            return self.file.name.split("/")[-1].split(".")[0]
        except (KeyError, IndexError):
            return "unnamed"

    @classmethod
    def create_from_file(cls, django_file, module):
        att = cls(module=module)
        att.position = module.attachments.all().count()
        att.file.save(django_file.name.split("/")[-1], django_file)
        att.save()
        return att

    class Meta:
        ordering = ("position",)


class ModuleSymlink(Module):
    admin_template_name = "xprez/admin/modules/module_symlink.html"
    icon_template_name = "xprez/admin/icons/modules/module_symlink.html"
    symlink = models.ForeignKey(
        Module,
        on_delete=models.SET_NULL,
        null=True,
        editable=False,
        related_name="symlinked_module_set",
    )

    class Meta:
        verbose_name = "Linked module"

    def render_front(self, *args, **kwargs):
        if self.symlink:
            return self.symlink.polymorph().render_front(*args, **kwargs)
        else:
            return ""


class SectionSymlink(Module):
    admin_template_name = "xprez/admin/modules/section_symlink.html"
    icon_template_name = "xprez/admin/icons/modules/section_symlink.html"
    symlink = models.ForeignKey(
        settings.XPREZ_SECTION_MODEL_CLASS,
        on_delete=models.SET_NULL,
        null=True,
        editable=False,
        related_name="symlinked_section_set",
    )

    class Meta:
        verbose_name = "Linked section"

    def render_front(self, context):
        if self.symlink:
            return self.symlink.render_front(context)
        else:
            return ""
