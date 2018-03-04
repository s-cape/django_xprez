from django import forms
from django.urls import reverse_lazy


class MediumEditorWidget(forms.widgets.Textarea):
    FULL = 'full'
    SIMPLE = 'simple'
    FULL_NO_INSERT_PLUGIN = 'full_no_insert_plugin'
    MODE_CHOICES = [FULL, SIMPLE, FULL_NO_INSERT_PLUGIN]

    class Media:
        css = {
            'all': (
                'xprez/admin/libs/medium-editor/dist/css/medium-editor.min.css',
                'xprez/admin/libs/medium-editor/dist/css/themes/default.min.css',
                'xprez/admin/libs/medium-editor-insert-plugin/dist/css/medium-editor-insert-plugin.min.css',
                'medium_editor/css/medium_editor_widget.css',
                "//netdna.bootstrapcdn.com/font-awesome/4.1.0/css/font-awesome.css",
            )
        }
        js = (
            'xprez/admin/libs/jquery/dist/jquery.min.js',
            'xprez/admin/libs/handlebars/handlebars.min.js',
            'xprez/admin/libs/medium-editor/dist/js/medium-editor.min.js',
            'xprez/admin/libs/jquery-sortable/source/js/jquery-sortable-min.js',
            'xprez/admin/libs/blueimp-file-upload/js/vendor/jquery.ui.widget.js',
            'xprez/admin/libs/blueimp-file-upload/js/jquery.iframe-transport.js',
            'xprez/admin/libs/blueimp-file-upload/js/jquery.fileupload.js',
            'xprez/admin/libs/medium-editor-insert-plugin/dist/js/medium-editor-insert-plugin.js',
            'xprez/admin/libs/rangy/rangy-core.js',
            'xprez/admin/libs/rangy/rangy-classapplier.js',
            'medium_editor/js/medium_editor_widget.js',
        )

    def __init__(self, mode='full', file_upload_dir=None, attrs=None):
        assert mode in self.MODE_CHOICES
        if mode == self.SIMPLE:
            css_class = 'medium-editor-simple ignore-changes'
        elif mode == self.FULL:
            css_class = 'medium-editor ignore-changes'
        else:
            css_class = 'medium-editor-no-insert-plugin'
        default_attrs = {'cols': '40', 'rows': '10', 'class': css_class, }
        if attrs:
            default_attrs.update(attrs)

        if file_upload_dir:
            default_attrs['data-file-upload'] = reverse_lazy('medium_file_upload', args=[file_upload_dir])
            default_attrs['data-file-delete'] = reverse_lazy('medium_file_delete')

        super(MediumEditorWidget, self).__init__(default_attrs)
