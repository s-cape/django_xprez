# -*- coding: utf-8 -*-
from os import makedirs, path

from django.conf import settings as django_settings
from django.contrib.admin.views.decorators import staff_member_required
from django.db import models
from django.db.models import JSONField
from django.http import JsonResponse
from django.template import TemplateDoesNotExist
from django.template.defaultfilters import striptags
from django.template.loader import get_template
from django.urls import re_path
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from xprez.utils import random_string

from .. import contents_manager, settings
from ..ck_editor import parse_text as ckeditor_parse_text
from ..ck_editor.widgets import CkEditorWidget
from ..medium_editor.utils import parse_text as medium_editor_parse_text
from ..medium_editor.utils import render_text_parsed as medium_editor_render_text_parsed
from ..medium_editor.widgets import MediumEditorWidget
from .base import AjaxUploadFormsetContent, Content, ContentItem, FormsetContent
from .fields import TemplatePathField

PHOTOSWIPE_JS = (
    "xprez/libs/photoswipe/dist/photoswipe.min.js",
    "xprez/libs/photoswipe/dist/photoswipe-ui-default.min.js",
    "xprez/js/photoswipe.js",
)
PHOTOSWIPE_CSS = (
    "xprez/libs/photoswipe/dist/photoswipe.css",
    "xprez/libs/photoswipe/dist/default-skin/default-skin.css",
)


class MediumEditor(Content):
    form_class = "xprez.admin_forms.MediumEditorForm"
    admin_template_name = "xprez/admin/contents/medium_editor.html"
    front_template_name = "xprez/contents/medium_editor.html"
    icon_name = "text_content"
    verbose_name = "Text Content"

    text = models.TextField()
    # css_class = models.CharField(max_length=100, null=True, blank=True)
    box = models.BooleanField(default=False)
    width = models.CharField(
        max_length=50, choices=Content.SIZE_CHOICES, default=Content.SIZE_FULL
    )

    class AdminMedia:
        js = MediumEditorWidget.Media.js
        css = MediumEditorWidget.Media.css["all"]

    def show_front(self):
        return striptags(self.text) != ""

    def get_parsed_text(self):
        return medium_editor_parse_text(self.text)

    def render_text(self):
        return medium_editor_render_text_parsed(self.get_parsed_text())


class CkEditorFileUploadMixin:
    @classmethod
    @method_decorator(staff_member_required)
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


class CkEditor(CkEditorFileUploadMixin, Content):
    form_class = "xprez.admin_forms.CkEditorForm"
    admin_template_name = "xprez/admin/contents/ck_editor.html"
    front_template_name = "xprez/contents/ck_editor.html"
    icon_name = "text_content"
    verbose_name = "Text Content"

    text = models.TextField()
    # css_class = models.CharField(max_length=100, null=True, blank=True)
    box = models.BooleanField(default=False)
    width = models.CharField(
        max_length=50, choices=Content.SIZE_CHOICES, default=Content.SIZE_TEXT
    )
    content_centered = models.BooleanField(default=False)

    class AdminMedia:
        js = CkEditorWidget.Media.js + PHOTOSWIPE_JS
        css = {"all": CkEditorWidget.Media.css["all"] + PHOTOSWIPE_CSS}

    def show_front(self):
        # TODO: not working for single image inserted in editor
        return striptags(self.text) != ""

    def render_front(self, extra_context={}):
        extra_context["parsed_text"] = ckeditor_parse_text.render_text_parsed(
            ckeditor_parse_text.parse_text(self.text, extra_context["request"])
        )
        return super().render_front(extra_context=extra_context)


class QuoteContent(FormsetContent):
    form_class = "xprez.admin_forms.QuoteContentForm"
    formset_factory = "xprez.admin_forms.QuoteFormSet"
    admin_template_name = "xprez/admin/contents/quote.html"
    front_template_name = "xprez/contents/quote.html"
    icon_name = "quote"
    verbose_name = "Quote"

    title = models.CharField(max_length=255, null=True, blank=True)
    box = models.BooleanField(default=False)

    display_two = models.BooleanField(default=False)

    def get_formset_queryset(self):
        return self.quotes.all()

    def show_front(self):
        quotes = self.quotes.all()
        if len(quotes) == 0:
            return False
        quote = quotes.first()
        if not quote.name or not quote.quote:
            return False
        return True


class Quote(ContentItem):
    content_foreign_key = "content"
    content = models.ForeignKey(
        QuoteContent, related_name="quotes", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    job_title = models.CharField(max_length=255)
    image = models.ImageField(upload_to="quotes", null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    quote = models.TextField()
    # position = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ("content", "id")


class Gallery(AjaxUploadFormsetContent):

    COLUMNS_CHOICES = (
        (1, "1"),
        (2, "2"),
        (3, "3"),
        (4, "4"),
        (6, "6"),
        (8, "8"),
    )

    form_class = "xprez.admin_forms.GalleryForm"
    admin_template_name = "xprez/admin/contents/gallery/gallery.html"
    admin_formset_item_template_name = "xprez/admin/contents/gallery/photo.html"
    front_template_name = "xprez/contents/gallery.html"
    icon_name = "gallery"
    verbose_name = "Gallery / Image"
    formset_factory = "xprez.admin_forms.PhotoFormSet"

    width = models.CharField(
        max_length=50, choices=Content.SIZE_CHOICES, default=Content.SIZE_FULL
    )
    columns = models.PositiveSmallIntegerField(default=1)
    divided = models.BooleanField(default=False)
    crop = models.BooleanField(default=False)

    def get_formset_queryset(self):
        return self.photos.all()

    def save_admin_form(self, request):
        super(Gallery, self).save_admin_form(request)
        for index, photo in enumerate(self.photos.all()):
            photo.position = index
            photo.save()

    class FrontMedia:
        js = PHOTOSWIPE_JS
        css = PHOTOSWIPE_CSS

    def show_front(self):
        return self.photos.all().count()


class Photo(ContentItem):
    content_foreign_key = "gallery"
    gallery = models.ForeignKey(
        Gallery, related_name="photos", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="photos")
    description = models.CharField(max_length=255, blank=True, null=True)
    alt_text = models.CharField(max_length=255, blank=True)
    position = models.PositiveSmallIntegerField()

    @classmethod
    def create_from_file(cls, django_file, gallery):
        photo = cls(gallery=gallery)
        photo.position = gallery.photos.all().count()
        photo.image.save(django_file.name.split("/")[-1], django_file)
        photo.save()
        return photo

    class Meta:
        ordering = ("position",)
        # unique_together = (
        #     ('gallery', 'position', )
        # )


class Video(Content):
    TYPE_CHOICES = (
        ("youtube", "YouTube"),
        ("vimeo", "Vimeo"),
    )
    admin_template_name = "xprez/admin/contents/video.html"
    front_template_name = "xprez/contents/video.html"
    verbose_name = "Video"
    icon_name = "video"
    form_class = "xprez.admin_forms.VideoForm"

    poster_image = models.ImageField(upload_to="video", null=True, blank=True)
    url = models.URLField()
    width = models.CharField(
        max_length=50, choices=Content.SIZE_CHOICES, default=Content.SIZE_FULL
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


class CodeInput(Content):
    admin_template_name = "xprez/admin/contents/code_input.html"
    front_template_name = "xprez/contents/code_input.html"
    verbose_name = "Code Input"
    icon_name = "code"
    form_class = "xprez.admin_forms.CodeInputForm"

    code = models.TextField()

    def show_front(self):
        return self.code


class NumbersContent(FormsetContent):
    admin_template_name = "xprez/admin/contents/numbers.html"
    front_template_name = "xprez/contents/numbers.html"
    verbose_name = "Numbers"
    icon_name = "numbers"
    form_class = "xprez.admin_forms.NumbersContentForm"
    formset_factory = "xprez.admin_forms.NumberFormSet"

    def get_formset_queryset(self):
        return self.numbers.all()

    def show_front(self):
        return self.numbers.all().count()

    class FrontMedia:
        js = (
            "xprez/libs/jquery.waypoints.min.js",
            "xprez/libs/counter.up/jquery.counterup.js",
            "xprez/js/numbers.js",
        )


class Number(ContentItem):
    content_foreign_key = "content"
    content = models.ForeignKey(
        NumbersContent, related_name="numbers", on_delete=models.CASCADE
    )
    number = models.IntegerField(null=True, blank=True)
    suffix = models.CharField(max_length=10, null=True, blank=True)
    title = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ("content", "id")


class FeatureBoxes(Content):
    admin_template_name = "xprez/admin/contents/feature_boxes.html"
    front_template_name = "xprez/contents/feature_boxes.html"
    verbose_name = "Feature Boxes"
    icon_name = "feature_boxes"
    form_class = "xprez.admin_forms.FeatureBoxesForm"

    box_1 = models.TextField(blank=True)
    box_2 = models.TextField(blank=True)
    box_3 = models.TextField(blank=True)

    def show_front(self):
        return bool(self.box_1)


class CodeTemplate(Content):
    admin_template_name = "xprez/admin/contents/code_template.html"
    verbose_name = "Code Template"
    icon_name = "code_template"
    form_class = "xprez.admin_forms.CodeTemplateForm"

    template_name = TemplatePathField(
        template_dir=settings.XPREZ_CODE_TEMPLATES_DIR,
        prefix=settings.XPREZ_CODE_TEMPLATES_PREFIX,
        max_length=255,
        null=True,
        blank=True,
    )

    def show_front(self):
        return self.template_name

    def render_front(self, extra_context=None):
        if self.show_front():
            context = extra_context or {}
            context["content"] = self
            try:
                return get_template(self.template_name).render(context=context)
            except TemplateDoesNotExist:
                return "Invalid Template"
        else:
            return ""


class DownloadContent(AjaxUploadFormsetContent):
    admin_template_name = "xprez/admin/contents/download/download.html"
    front_template_name = "xprez/contents/download.html"
    admin_formset_item_template_name = "xprez/admin/contents/download/attachment.html"

    verbose_name = "Files"
    icon_name = "files"
    form_class = "xprez.admin_forms.DownloadContentForm"
    formset_factory = "xprez.admin_forms.AttachmentFormSet"

    title = models.CharField(max_length=255, blank=True)

    def get_formset_queryset(self):
        return self.attachments.all()

    def show_front(self):
        return self.attachments.all().count()


class Attachment(ContentItem):
    content_foreign_key = "content"
    content = models.ForeignKey(
        DownloadContent, related_name="attachments", on_delete=models.CASCADE
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
    def create_from_file(cls, django_file, content):
        att = cls(content=content)
        att.position = content.attachments.all().count()
        att.file.save(django_file.name.split("/")[-1], django_file)
        att.save()
        return att

    class Meta:
        ordering = ("position",)


class TextImageBase(Content):
    form_class = "xprez.admin_forms.TextImageForm"
    admin_template_name = "xprez/admin/contents/text_image.html"
    front_template_name = "xprez/contents/text_image.html"
    verbose_name = "Image + Text"
    icon_name = "text_image"

    ALIGNMENT_LEFT = "left"
    ALIGNMENT_RIGHT = "right"
    IMAGE_ALIGNMENT_CHOICES = (
        (ALIGNMENT_LEFT, "Left"),
        (ALIGNMENT_RIGHT, "Right"),
    )

    image = models.ImageField(upload_to="text_image_images")
    text = models.TextField()
    image_alignment = models.CharField(
        choices=IMAGE_ALIGNMENT_CHOICES, default=ALIGNMENT_LEFT, max_length=15
    )
    # css_class = models.CharField(max_length=100, null=True, blank=True)

    class AdminMedia:
        js = CkEditorWidget.Media.js
        css = {"css": CkEditorWidget.Media.css["all"]}

    class Meta:
        abstract = True

    def show_front(self):
        return True

    def render_front(self, extra_context={}):
        extra_context["parsed_text"] = ckeditor_parse_text.render_text_parsed(
            ckeditor_parse_text.parse_text(self.text, extra_context["request"])
        )
        return super().render_front(extra_context=extra_context)

    # def show_front(self):
    #     return striptags(self.text) != ''

    # def get_parsed_text(self):
    #     return medium_editor_parse_text(self.text)

    # def render_text(self):
    #     return medium_editor_render_text_parsed(self.get_parsed_text())


class TextImage(TextImageBase):
    class Meta:
        abstract = False


class GridBoxes(CkEditorFileUploadMixin, Content):
    form_class = "xprez.admin_forms.GridBoxesForm"
    admin_template_name = "xprez/admin/contents/grid_boxes/grid_boxes.html"
    front_template_name = "xprez/contents/grid_boxes.html"
    verbose_name = "Grid Boxes"
    icon_name = "grid_boxes"

    MARGIN_CHOICES = (
        ("none", "none"),
        ("m", "m"),
        ("l", "l"),
    )

    TEXT_SIZE_CHOICES = (
        ("xs", "xs"),
        ("s", "s"),
        ("m", "m"),
    )

    class AdminMedia:
        js = CkEditorWidget.Media.js + ("xprez/admin/js/grid_boxes.js",)
        css = {"css": CkEditorWidget.Media.css["all"]}

    columns = models.PositiveSmallIntegerField(default=2)
    margin = models.CharField(max_length=4, choices=MARGIN_CHOICES, default="m")
    width = models.CharField(
        max_length=50, choices=Content.SIZE_CHOICES, default=Content.SIZE_FULL
    )
    text_size = models.CharField(max_length=2, choices=TEXT_SIZE_CHOICES, default="m")

    padded = models.BooleanField(default=True)
    content_centered = models.BooleanField(default=False)
    edge_images = models.BooleanField(default=False)
    boxes_filled = models.BooleanField(default=True)
    border = models.BooleanField(default=True)
    boxes = JSONField(null=True)

    def render_front(self, extra_context={}):
        boxes = []
        for box_content in self.boxes or []:
            if striptags(box_content != ""):
                # boxes.append(medium_editor_render_text_parsed(medium_editor_parse_text(box_content)))
                boxes.append(
                    ckeditor_parse_text.render_text_parsed(
                        ckeditor_parse_text.parse_text(
                            box_content, extra_context["request"]
                        )
                    )
                )

        extra_context["rendered_boxes"] = boxes
        return super().render_front(extra_context=extra_context)

    def show_front(self):
        for box_content in self.boxes or []:
            if striptags(box_content != ""):
                return True
        return False


contents_manager.register(MediumEditor)
contents_manager.register(CkEditor)
contents_manager.register(QuoteContent)
contents_manager.register(Gallery)
contents_manager.register(DownloadContent)
contents_manager.register(Video)
contents_manager.register(NumbersContent)
contents_manager.register(FeatureBoxes)
contents_manager.register(CodeInput)
contents_manager.register(CodeTemplate)
contents_manager.register(TextImage)
contents_manager.register(GridBoxes)
