import mimetypes

from django import forms
from django.db import models
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _

from xprez import constants
from xprez.admin.forms import ModuleForm
from xprez.ck_editor import parse_text as ckeditor_parse_text
from xprez.ck_editor.forms import CkEditorFileUploadXprezAdminFormMixin
from xprez.ck_editor.widgets import CkEditorWidget
from xprez.conf import defaults, settings
from xprez.models.configs import ModuleConfig
from xprez.models.mixins.font_size import FontSizeModuleMixin
from xprez.models.mixins.responsive_image import (
    ResponsiveImageMixin,
    ResponsiveImageSourcesMixin,
)
from xprez.models.modules import Module
from xprez.utils import import_class, truncate_with_ellipsis


class TextModuleBase(FontSizeModuleMixin, Module):
    config_model = "xprez.TextBaseConfig"
    front_template_name = "xprez/modules/text_base.html"
    admin_template_name = "xprez/admin/modules/text_base.html"
    admin_form_class = "xprez.modules.text.TextModuleBaseForm"
    admin_icon_template_name = "xprez/shared/icons/modules/text_base.html"

    text = models.TextField(blank=True)

    class Meta:
        abstract = True


class TextModule(ResponsiveImageSourcesMixin, ResponsiveImageMixin, TextModuleBase):
    front_cacheable = True
    config_model = "xprez.TextConfig"
    front_template_name = "xprez/modules/text.html"
    admin_template_name = "xprez/admin/modules/text.html"
    admin_form_class = "xprez.modules.text.TextModuleForm"
    admin_icon_template_name = "xprez/shared/icons/modules/text.html"
    admin_js_controller_class = "XprezTextModule"

    media = models.FileField(upload_to="images", null=True, blank=True)
    url = models.CharField(_("Target URL"), max_length=255, null=True, blank=True)

    class AdminMedia:
        js = CkEditorWidget.Media.js
        css = {"css": CkEditorWidget.Media.css["all"]}

    class FrontMedia:
        js = ("xprez/js/observer_autoplay.min.js",)

    class Meta:
        verbose_name = _("Text")

    def get_media_extension(self):
        name = self.media.name or ""
        if "." in name:
            return name.rsplit(".", 1)[-1].lower()
        else:
            return ""

    IMAGE_EXTENSIONS = settings.XPREZ_IMAGE_EXTENSIONS
    VIDEO_EXTENSIONS = settings.XPREZ_VIDEO_EXTENSIONS

    @property
    def media_is_image(self):
        return self.get_media_extension() in self.IMAGE_EXTENSIONS

    @property
    def media_is_video(self):
        return self.get_media_extension() in self.VIDEO_EXTENSIONS

    @property
    def media_mime_type(self):
        mime, _ = mimetypes.guess_type(self.media.name)
        return mime or ""

    def get_image_field(self):
        return self.media

    def get_config_crop(self, config):
        return config.media_crop if config else None

    def get_image_aspect_ratio(self):
        """Base-config crop ratio for srcset_geometries; falls back to (1, 1)."""
        config = self.configs.filter(css_breakpoint=0).first()
        crop = self.parse_crop_string(self.get_config_crop(config))
        if crop:
            return crop
        else:
            return (1, 1)

    def render_front(self, context):
        context["parsed_text"] = ckeditor_parse_text.render_text_parsed(
            ckeditor_parse_text.parse_text(self.text, context["request"])
        )
        return super().render_front(context)

    def preview_text(self):
        return truncate_with_ellipsis(
            strip_tags(self.text), constants.PREVIEW_TEXT_MAX_LENGTH
        )


class TextBaseConfig(ModuleConfig):
    admin_template_name = "xprez/admin/configs/modules/text_base.html"

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

    def get_css_variables(self):
        variables = super().get_css_variables()
        variables["text-align"] = self.text_align
        return variables


class TextConfig(TextBaseConfig):
    admin_template_name = "xprez/admin/configs/modules/text.html"

    media_role = models.CharField(
        _("Media role"),
        max_length=20,
        choices=constants.MEDIA_ROLE_CHOICES,
        default=defaults.XPREZ_DEFAULTS["module_config"]["xprez.TextModule"][
            "media_role"
        ],
    )
    media_background_position = models.CharField(
        max_length=10,
        choices=constants.BACKGROUND_POSITION_CHOICES,
        default=defaults.XPREZ_DEFAULTS["module_config"]["xprez.TextModule"][
            "media_background_position"
        ],
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
    media_border_radius_choice = models.CharField(
        _("Media border radius"),
        max_length=20,
        choices=constants.BORDER_RADIUS_CHOICES,
        default=defaults.XPREZ_DEFAULTS["module_config"]["xprez.TextModule"][
            "media_border_radius_choice"
        ],
        blank=True,
    )
    media_border_radius_custom = models.PositiveIntegerField(
        null=True,
        blank=True,
        default=defaults.XPREZ_DEFAULTS["module_config"]["xprez.TextModule"][
            "media_border_radius_custom"
        ],
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
                variables["media-icon-max-size"] = self._format_css_field(
                    "media_icon_max_size"
                )

            if self.media_role in [
                constants.MEDIA_ROLE_LEAD,
                constants.MEDIA_ROLE_ICON,
            ]:
                variables["media-border-radius"] = self._get_choice_or_custom(
                    "media_border_radius"
                )

            if self.media_role == constants.MEDIA_ROLE_BACKGROUND:
                variables["background-position"] = self.media_background_position

            if self.media_lead_to_edge:
                variables["padding-top"] = self._get_choice_or_custom("padding_top")
                variables["padding-right"] = self._get_choice_or_custom("padding_right")
                variables["padding-left"] = self._get_choice_or_custom("padding_left")

        return variables


class TextModuleBaseForm(CkEditorFileUploadXprezAdminFormMixin, ModuleForm):
    options_fields = ModuleForm.options_fields + ("font_size",)

    class Meta:
        model = TextModuleBase
        fields = "__all__"
        widgets = {
            "text": import_class(settings.XPREZ_CK_EDITOR_MODULE_WIDGET),
        }


class TextModuleForm(TextModuleBaseForm):
    options_fields = TextModuleBaseForm.options_fields + ("url",)
    sync_exclude = TextModuleBaseForm.sync_exclude + ("url",)
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
        fields = "__all__"
