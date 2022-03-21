from copy import deepcopy

DEFAULT_ALLOWED_CONTENTS = [
    # 'mediumeditor',
    'ckeditor',
    'quotecontent',
    'gallery',
    'downloadcontent',
    'video',
    'numberscontent',
    'featureboxes',
    'codeinput',
    'codetemplate',
    'textimage',
]

XPREZ_CKEDITOR_CONFIG_SIMPLE = {
    'toolbar': ('bold', 'italic', 'link'),
    'blockToolbar': (),
}

_XPREZ_CKEDITOR_CONFIG_FULL_BASE = {
    'blockToolbar': ('heading', '|', 'blockQuote', 'bulletedList', 'numberedList',),
    'toolbar': ('bold', 'italic', 'link', '|', 'heading', '|', 'blockQuote', 'bulletedList', 'numberedList',),
    'placeholder': 'Type your text',
    'link': {
        'decorators': {
            'toggleButtonPrimary': {
                'mode': 'manual',
                'label': 'Primary button',
                'attributes': {
                    'class': 'btn btn-primary'
                }
            },
            'toggleButtonSecondary': {
                'mode': 'manual',
                'label': 'Secondary button',
                'attributes': {
                    'class': 'btn btn-secondary'
                }
            },
            'openInNewTab': {
                'mode': 'manual',
                'label': 'Open in a new tab',
                'defaultValue': False,
                'attributes': {
                    'target': '_blank',
                }
            }
        }
    },
    'heading': {
        'options': (
            {'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph'},
            {'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2'},
            {'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3'},
        ),
    },
    'fontSize': {
        'options': ('tiny', 'default', 'big',)
    },

}

XPREZ_CKEDITOR_CONFIG_FULL_NO_INSERT_PLUGIN = deepcopy(_XPREZ_CKEDITOR_CONFIG_FULL_BASE)
XPREZ_CKEDITOR_CONFIG_FULL_NO_INSERT_PLUGIN['image'] = {
    'toolbar': ('|',)
}

XPREZ_CKEDITOR_CONFIG_FULL = deepcopy(_XPREZ_CKEDITOR_CONFIG_FULL_BASE)
XPREZ_CKEDITOR_CONFIG_FULL['blockToolbar'] += ('|', 'imageUpload', 'MediaEmbed',)
XPREZ_CKEDITOR_CONFIG_FULL['toolbar'] += ('|', 'imageUpload', 'MediaEmbed',)
XPREZ_CKEDITOR_CONFIG_FULL['simpleUpload'] = {'uploadUrl': None}  # filled later in CkEditor.__init__
XPREZ_CKEDITOR_CONFIG_FULL['mediaEmbed '] = {'previewsInData': True}
XPREZ_CKEDITOR_CONFIG_FULL['image'] = {
    'toolbar': ('imageTextAlternative', 'toggleImageCaption', '|', 'imageStyle:alignLeft', 'imageStyle:block', 'imageStyle:alignRight', '|', 'linkImage',),
    'styles': ('block', 'alignLeft', 'alignRight',),
}
