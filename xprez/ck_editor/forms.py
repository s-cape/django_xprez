from .widgets import CkEditorFileUploadWidgetMixin


class CkEditorFileUploadFormMixin:
    """Bind file_upload_url_name and file_upload_dir to file-upload widgets.
    Override the getters to supply values; default is None for all.
    """

    def xprez_ckeditor_file_upload_url_name(self):
        return None

    def xprez_ckeditor_file_upload_dir(self):
        return None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bind_ckeditor_file_upload_widgets()

    # def xprez_ckeditor_file_upload_url_name(self):
    #     return xprez_settings.XPREZ_CK_EDITOR_FILE_UPLOAD_URL_NAME

    # def xprez_ckeditor_file_upload_dir(self):
    #     return xprez_settings.XPREZ_CK_EDITOR_FILE_UPLOAD_DIR

    def _bind_ckeditor_file_upload_widgets(self):
        url_name = self.xprez_ckeditor_file_upload_url_name()
        upload_dir = self.xprez_ckeditor_file_upload_dir()
        for field in self.fields.values():
            if isinstance(field.widget, CkEditorFileUploadWidgetMixin):
                field.widget.file_upload_url_name = url_name
                field.widget.file_upload_dir = upload_dir


class CkEditorFileUploadXprezAdminFormMixin(CkEditorFileUploadFormMixin):
    """Supply upload options from form.xprez_admin."""

    def xprez_ckeditor_file_upload_url_name(self):
        return self.xprez_admin.xprez_ckeditor_file_upload_url_name()

    def xprez_ckeditor_file_upload_dir(self):
        return self.xprez_admin.xprez_ckeditor_file_upload_dir()
