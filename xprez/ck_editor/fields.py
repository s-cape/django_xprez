from django.db import models
from django.utils.html import strip_tags

from . import widgets


class HtmlField(models.TextField):
    def clean(self, *args, **kwargs):
        value = super().clean(*args, **kwargs)
        if value and not strip_tags(value):
            value = ""

        return value


class CkEditorFieldSimple(HtmlField):
    def formfield(self, **kwargs):
        kwargs["widget"] = widgets.CkEditorWidgetSimple
        return super().formfield(**kwargs)


class CkEditorFieldFullNoInsertPlugin(HtmlField):
    def formfield(self, **kwargs):
        kwargs["widget"] = widgets.CkEditorWidgetNoInsertPlugin
        return super().formfield(**kwargs)


class CkEditorFileUploadFieldMixin:
    """Provide file_upload_url_name and file_upload_dir for CKEditor widget."""

    def __init__(self, *args, **kwargs):
        if "file_upload_url_name" in kwargs:
            self.file_upload_url_name = kwargs.pop("file_upload_url_name")
        if "file_upload_dir" in kwargs:
            self.file_upload_dir = kwargs.pop("file_upload_dir")
        super().__init__(*args, **kwargs)

    def get_file_upload_url_name(self):
        return getattr(self, "file_upload_url_name", None)

    def get_file_upload_dir(self):
        return getattr(self, "file_upload_dir", None)

    def formfield(self, **kwargs):
        kwargs["widget"] = self.file_upload_widget_class(
            file_upload_url_name=self.get_file_upload_url_name(),
            file_upload_dir=self.get_file_upload_dir(),
        )
        return super().formfield(**kwargs)


class CkEditorFieldFull(CkEditorFileUploadFieldMixin, HtmlField):
    file_upload_widget_class = widgets.CkEditorWidgetFull


class CkEditorFieldFullWithTable(CkEditorFieldFull):
    file_upload_widget_class = widgets.CkEditorWidgetFullWithTable


CkEditorField = CkEditorFieldFull
