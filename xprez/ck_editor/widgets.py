from django import forms
from django.urls import reverse_lazy


class CkEditorWidget(forms.widgets.Textarea):
    FULL = 'full'
    SIMPLE = 'simple'
    FULL_NO_INSERT_PLUGIN = 'full_no_insert_plugin'
    MODE_CHOICES = [FULL, SIMPLE, FULL_NO_INSERT_PLUGIN]

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

    def __init__(self, mode='full', file_upload_dir=None, attrs=None):
        assert mode in self.MODE_CHOICES
        default_attrs = {
            'class': 'js-ck-editor-source',
            'data-ck-editor-variant': mode,
            'cols': '40', 'rows': '10',
        }
        if attrs:
            default_attrs.update(attrs)

        if file_upload_dir:
            default_attrs['data-file-upload'] = reverse_lazy('xprez:ckeditor_file_upload', args=[file_upload_dir])

        super(CkEditorWidget, self).__init__(default_attrs)
