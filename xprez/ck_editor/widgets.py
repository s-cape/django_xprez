import json

from django import forms
from django.urls import reverse
from xprez import settings


class CkEditorWidget(forms.widgets.Textarea):
    template_name = 'xprez/widgets/ck_editor.html'

    class Media:
        css = {
            'all': (
                # 'ck_editor/css/ck_editor_widget.css',
            )
        }
        js = (
            'xprez/admin/libs/jquery/dist/jquery.min.js',
            'ck_editor/libs/ck_editor/ckeditor.js',
            'ck_editor/js/ck_editor_widget.js',
        )

    def __init__(self, config=None, file_upload_dir=None, attrs=None):
        if config is None:
            config = settings.XPREZ_CKEDITOR_CONFIG_FULL

        if 'simpleUpload' in config and config['simpleUpload'].get('uploadUrl') is None:
            config['simpleUpload']['uploadUrl'] = reverse('xprez:ckeditor_file_upload', args=[file_upload_dir])

        default_attrs = {
            'class': 'js-ck-editor-source',
            'data-ck-editor-config': json.dumps(config),
        }
        if attrs:
            default_attrs.update(attrs)

        super(CkEditorWidget, self).__init__(default_attrs)
