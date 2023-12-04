import json

from django import forms
from django.urls import reverse
from xprez.conf import settings


class CkEditorWidgetBase(forms.widgets.Textarea):
    template_name = "xprez/widgets/ck_editor.html"

    def get_config(self, file_upload_dir=None):
        raise NotImplementedError

    class Media:
        css = {"all": ()}
        js = tuple(settings.XPREZ_JQUERY_INIT_MEDIA_JS) + (
            "ck_editor/libs/ck_editor/ckeditor.js",
            "ck_editor/js/ck_editor_widget.js",
        )

    def __init__(self, file_upload_dir=None, attrs=None):
        config = self.get_config(file_upload_dir=None)

        default_attrs = {
            "class": "js-ck-editor-source",
            "data-ck-editor-config": json.dumps(config),
        }
        if attrs:
            default_attrs.update(attrs)

        super().__init__(default_attrs)


class CkEditorWidgetSimple(CkEditorWidgetBase):
    def get_config(self, *args, **kwargs):
        return {
            "toolbar": ("bold", "italic", "link"),
            "blockToolbar": (),
        }


class CkEditorWidgetFullBase(CkEditorWidgetBase):
    def get_config(self, *args, **kwargs):
        return {
            "blockToolbar": (
                "heading",
                "|",
                "blockQuote",
                "bulletedList",
                "numberedList",
            ),
            "toolbar": (
                "bold",
                "italic",
                "link",
                "|",
                "heading",
                "|",
                "blockQuote",
                "bulletedList",
                "numberedList",
            ),
            "placeholder": "Type your text",
            "link": {
                "decorators": {
                    "toggleButtonPrimary": {
                        "mode": "manual",
                        "label": "Primary button",
                        "classes": ["btn", "btn-primary"],
                    },
                    "toggleButtonSecondary": {
                        "mode": "manual",
                        "label": "Secondary button",
                        "classes": ["btn", "btn-secondary"],
                    },
                    "openInNewTab": {
                        "mode": "manual",
                        "label": "Open in a new tab",
                        "defaultValue": False,
                        "attributes": {
                            "target": "_blank",
                        },
                    },
                }
            },
            "heading": {
                "options": (
                    {
                        "model": "paragraph",
                        "title": "Paragraph",
                        "class": "ck-heading_paragraph",
                    },
                    {
                        "model": "heading2",
                        "view": "h2",
                        "title": "Heading 2",
                        "class": "ck-heading_heading2",
                    },
                    {
                        "model": "heading3",
                        "view": "h3",
                        "title": "Heading 3",
                        "class": "ck-heading_heading3",
                    },
                ),
            },
            "fontSize": {
                "options": (
                    "tiny",
                    "default",
                    "big",
                )
            },
        }


class CkEditorWidgetFullNoInsertPlugin(CkEditorWidgetFullBase):
    def get_config(self, *args, **kwargs):
        config = super().get_config(*args, **kwargs)
        config["image"] = {"toolbar": ("|",)}
        return config


class CkEditorWidgetFull(CkEditorWidgetFullBase):
    def get_config(self, file_upload_dir, *args, **kwargs):
        config = super().get_config(*args, **kwargs)
        config["blockToolbar"] += (
            "|",
            "imageUpload",
            "MediaEmbed",
        )
        config["toolbar"] += (
            "|",
            "imageUpload",
            "MediaEmbed",
        )
        config["simpleUpload"] = {
            "uploadUrl": reverse("xprez:ckeditor_file_upload", args=[file_upload_dir])
        }
        config["mediaEmbed "] = {"previewsInData": True}
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


CkEditorWidget = CkEditorWidgetFull
