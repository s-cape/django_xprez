from os import makedirs, path

from django import forms
from django.conf import settings as django_settings
from django.db import models
from django.http import JsonResponse
from django.urls import re_path
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from xprez import constants
from xprez.admin.forms import BaseModuleForm
from xprez.admin.permissions import xprez_staff_member_required
from xprez.ck_editor import parse_text as ckeditor_parse_text
from xprez.ck_editor.widgets import CkEditorWidget
from xprez.conf import defaults, settings
from xprez.models.configs import ModuleConfig
from xprez.models.modules import CLIPBOARD_TEXT_MAX_LENGTH, Module
from xprez.utils import import_class, random_string, truncate_with_ellipsis


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
    def get_admin_urls(cls):
        cls_name = cls.__name__.lower()
        return [
            re_path(
                r"^{}/file-upload/(?P<directory>[/\w-]+)/$".format(cls_name),
                cls.file_upload_view,
                name="{}_file_upload".format(cls_name),
            ),
        ]


class TextModuleBase(CkEditorFileUploadMixin, Module):
    form_class = "xprez.modules.text.TextModuleBaseForm"
    admin_template_name = "xprez/admin/modules/text_base.html"
    front_template_name = "xprez/modules/text_base.html"
    icon_template_name = "xprez/admin/icons/modules/text_base.html"
    config_model = "xprez.TextBaseConfig"

    text = models.TextField(blank=True)

    class Meta:
        abstract = True


class TextModule(TextModuleBase):
    form_class = "xprez.modules.text.TextModuleForm"
    admin_template_name = "xprez/admin/modules/text.html"
    front_template_name = "xprez/modules/text.html"
    icon_template_name = "xprez/admin/icons/modules/text.html"
    config_model = "xprez.TextConfig"

    media = models.FileField(upload_to="images", null=True, blank=True)
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


class TextBaseConfig(ModuleConfig):
    admin_template_name = "xprez/admin/configs/modules/text_base.html"

    font_size = models.CharField(
        "Font size",
        max_length=20,
        choices=constants.FONT_SIZE_CHOICES,
        default=defaults.XPREZ_DEFAULTS["module_config"]["xprez.TextModule"][
            "font_size"
        ],
    )
    text_align = models.CharField(
        "Text align",
        max_length=20,
        choices=constants.TEXT_ALIGN_CHOICES,
        default=defaults.XPREZ_DEFAULTS["module_config"]["xprez.TextModule"][
            "text_align"
        ],
    )

    class Meta(ModuleConfig.Meta):
        abstract = True

    def get_css_classes(self):
        classes = super().get_css_classes()
        classes["font-size"] = self.font_size
        return classes

    def get_css_variables(self):
        variables = super().get_css_variables()
        variables["text-align"] = self.text_align
        return variables


class TextConfig(TextBaseConfig):
    admin_template_name = "xprez/admin/configs/modules/text.html"

    media_role = models.CharField(
        "Media role",
        max_length=20,
        choices=constants.MEDIA_ROLE_CHOICES,
        default=defaults.XPREZ_DEFAULTS["module_config"]["xprez.TextModule"][
            "media_role"
        ],
    )
    media_background_position = models.PositiveIntegerField(
        default=defaults.XPREZ_DEFAULTS["module_config"]["xprez.TextModule"][
            "media_background_position"
        ]
    )
    media_lead_to_edge = models.BooleanField(
        default=defaults.XPREZ_DEFAULTS["module_config"]["xprez.TextModule"][
            "media_lead_to_edge"
        ]
    )
    media_icon_max_size = models.PositiveIntegerField(
        default=defaults.XPREZ_DEFAULTS["module_config"]["xprez.TextModule"][
            "media_icon_max_size"
        ]
    )
    media_crop = models.CharField(
        max_length=5,
        choices=constants.CROP_CHOICES,
        default=defaults.XPREZ_DEFAULTS["module_config"]["xprez.TextModule"][
            "media_crop"
        ],
        blank=True,
    )

    def get_css_classes(self):
        classes = super().get_css_classes()
        if self.module.polymorph.media:
            classes["media-role"] = self.media_role
            if self.media_role == constants.MEDIA_ROLE_LEAD:
                classes["media-lead-to-edge"] = self.media_lead_to_edge
        return classes

    def get_css_variables(self):
        variables = super().get_css_variables()
        if self.module.polymorph.media:
            if self.media_role == constants.MEDIA_ROLE_LEAD and self.media_crop:
                variables["media-crop"] = self.media_crop
            if self.media_role == constants.MEDIA_ROLE_ICON:
                variables["media-icon-max-size"] = self.media_icon_max_size
            if self.media_role == constants.MEDIA_ROLE_BACKGROUND:
                variables["background-position"] = self.media_background_position

        return variables


class TextModuleBaseForm(BaseModuleForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        widget_class = import_class(settings.XPREZ_CK_EDITOR_MODULE_WIDGET)
        self.fields["text"].widget = widget_class(file_upload_dir="ck_editor_uploads")

    class Meta:
        model = TextModuleBase
        fields = ("text",) + BaseModuleForm.base_module_fields


class TextModuleForm(TextModuleBaseForm):
    options_fields = ("url",) + TextModuleBaseForm.options_fields
    media_clear = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["media"].widget = forms.FileInput()

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data.get("media_clear"):
            instance.media = None
        if commit:
            instance.save()
        return instance

    class Meta(TextModuleBaseForm.Meta):
        model = TextModule
        fields = TextModuleBaseForm.Meta.fields + ("media", "url")
