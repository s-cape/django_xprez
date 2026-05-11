from django.urls import path

from xprez.ck_editor.views import _ckeditor_file_upload
from xprez.conf import settings


class XprezAdminViewsCkEditorUploadMixin:
    def xprez_ckeditor_file_upload_view(self, *args, **kwargs):
        return _ckeditor_file_upload(*args, **kwargs)

    def xprez_ckeditor_file_upload_url_name(self):
        return self.xprez_admin_url_name("ckeditor_file_upload", include_namespace=True)

    def xprez_ckeditor_file_upload_dir(self):
        return getattr(settings, "XPREZ_CK_EDITOR_FILE_UPLOAD_DIR", None)

    def xprez_admin_urls(self):
        return [
            path(
                "xprez-ckeditor-file-upload/<str:directory>/",
                self.xprez_admin_view(self.xprez_ckeditor_file_upload_view),
                name=self.xprez_admin_url_name("ckeditor_file_upload"),
            ),
        ]
