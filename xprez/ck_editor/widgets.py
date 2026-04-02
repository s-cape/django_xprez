import copy
import json

from django import forms
from django.urls import reverse

from xprez.conf import settings


class CkEditorWidgetBase(forms.widgets.Textarea):
    template_name = "xprez/admin/widgets/ck_editor.html"

    def get_config(self, *args, **kwargs):
        raise NotImplementedError

    class Media:
        css = {"all": ()}
        js = (
            "ck_editor/libs/ck_editor/ckeditor.js",
            "ck_editor/js/ck_editor_widget.js",
        )

    def __init__(self, attrs=None):
        default_attrs = {"class": "js-ck-editor-source"}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

    def render(self, name, value, attrs=None, renderer=None):
        if attrs is None:
            attrs = {}
        attrs["data-ck-editor-config"] = json.dumps(self.get_config())
        return super().render(name, value, attrs=attrs, renderer=renderer)


class CkEditorWidgetSimple(CkEditorWidgetBase):
    def get_config(self, *args, **kwargs):
        return copy.deepcopy(settings.XPREZ_CK_EDITOR_SIMPLE_CONFIG)


class CkEditorWidgetFull(CkEditorWidgetBase):
    def get_config(self, *args, **kwargs):
        return copy.deepcopy(settings.XPREZ_CK_EDITOR_FULL_CONFIG)


class CkEditorFileUploadWidgetMixin:
    """Build upload URL from file_upload_url_name + file_upload_dir."""

    def __init__(self, **kwargs):
        if "file_upload_url_name" in kwargs:
            self.file_upload_url_name = kwargs.pop("file_upload_url_name")
        if "file_upload_dir" in kwargs:
            self.file_upload_dir = kwargs.pop("file_upload_dir")
        super().__init__(**kwargs)

    def get_file_upload_url(self):
        url_name = getattr(self, "file_upload_url_name", None) or getattr(
            settings, "XPREZ_CK_EDITOR_FILE_UPLOAD_URL_NAME", None
        )
        directory = getattr(self, "file_upload_dir", None) or getattr(
            settings, "XPREZ_CK_EDITOR_FILE_UPLOAD_DIR", None
        )
        if not url_name or not directory:
            raise ValueError(
                "CKEditor file upload requires file_upload_url_name and "
                "file_upload_dir (set on the widget or via "
                "XPREZ_CK_EDITOR_FILE_UPLOAD_URL_NAME and "
                "XPREZ_CK_EDITOR_FILE_UPLOAD_DIR settings)."
            )
        return reverse(url_name, args=[directory])

    def get_config(self, *args, **kwargs):
        config = super().get_config(*args, **kwargs)
        config["blockToolbar"] += ("|", "imageUpload")
        config["toolbar"] += ("|", "imageUpload")
        config["simpleUpload"] = {
            "uploadUrl": self.get_file_upload_url(),
        }
        config["image"] = {
            "toolbar": (
                "imageTextAlternative",
                "toggleImageCaption",
                "|",
                "imageStyle:alignLeft",
                "imageStyle:block",
                "imageStyle:alignRight",
                "|",
                "linkImage",
            ),
            "styles": (
                "block",
                "alignLeft",
                "alignRight",
            ),
        }
        return config


class CkEditorTableMixin:
    """Adds table toolbar and config to any CKEditor widget."""

    def get_config(self, *args, **kwargs):
        config = super().get_config(*args, **kwargs)
        config["toolbar"] += ("|", "insertTable")
        config["blockToolbar"] += ("|", "insertTable")
        config["table"] = {
            "contentToolbar": (
                "tableColumn",
                "tableRow",
                "mergeTableCells",
            ),
        }
        return config


class CkEditorWidgetFullWithUpload(CkEditorFileUploadWidgetMixin, CkEditorWidgetFull):
    """Full editor with image upload and MediaEmbed."""

    def get_config(self, *args, **kwargs):
        config = super().get_config(*args, **kwargs)
        config["blockToolbar"] += ("MediaEmbed",)
        config["toolbar"] += ("MediaEmbed",)
        config["mediaEmbed"] = {"previewsInData": True}
        return config


class CkEditorWidgetFullWithTable(CkEditorTableMixin, CkEditorWidgetFull):
    """Full editor with table support, without image insert."""

    pass


class CkEditorWidgetFullWithUploadAndTable(
    CkEditorTableMixin, CkEditorWidgetFullWithUpload
):
    """Full editor with image upload, MediaEmbed, and table support."""

    pass


CkEditorWidget = CkEditorWidgetFull
