"""The HTML a rich text field accepts over MCP, derived from its CKEditor config.

Each toolbar item stands for the markup it produces, so the rules follow the
editor's config (``XPREZ_CK_EDITOR_*_CONFIG`` and the widget's mixins): what
an editor cannot produce in the admin, an MCP client cannot send either.
"""

from dataclasses import dataclass, field

from django.urls import NoReverseMatch

from xprez.ck_editor.widgets import CkEditorFileUploadWidgetMixin, CkEditorTableMixin
from xprez.conf import settings
from xprez.utils import import_class

ALWAYS = ("p", "br")

# toolbar item -> the tags it produces; items not listed add nothing
TOOLBAR_TAGS = {
    "bold": ("strong",),
    "italic": ("em",),
    "underline": ("u",),
    "strikethrough": ("s",),
    "code": ("code",),
    "subscript": ("sub",),
    "superscript": ("sup",),
    "link": ("a",),
    "blockQuote": ("blockquote",),
    "bulletedList": ("ul", "li"),
    "numberedList": ("ol", "li"),
    "horizontalLine": ("hr",),
    "insertTable": ("figure", "table", "thead", "tbody", "tr", "th", "td"),
}


@dataclass
class TextRules:
    tags: list = field(default_factory=list)
    attributes: dict = field(default_factory=dict)  # tag -> attribute names
    classes: dict = field(default_factory=dict)  # tag -> class names

    def as_dict(self):
        return {
            "tags": self.tags,
            "attributes": self.attributes,
            "classes": self.classes,
        }


def text_rules(widget):
    config = editor_config(widget)
    tags = list(ALWAYS)
    attributes, classes = {}, {}
    toolbar = list(config.get("toolbar", ())) + list(config.get("blockToolbar", ()))
    for item in toolbar:
        if item == "heading":
            options = config.get("heading", {}).get("options", ())
            tags += [option["view"] for option in options if "view" in option]
        tags += TOOLBAR_TAGS.get(item, ())
    if "a" in tags:
        attributes["a"] = ["href"]
        for decorator in config.get("link", {}).get("decorators", {}).values():
            attributes["a"] += list(decorator.get("attributes", {}))
            classes.setdefault("a", [])
            classes["a"] += list(decorator.get("classes", ()))
    return TextRules(
        tags=_unique(tags),
        attributes={tag: _unique(names) for tag, names in attributes.items()},
        classes={tag: _unique(names) for tag, names in classes.items() if names},
    )


def module_text_rules():
    """The rules of the text module's editor (``XPREZ_CK_EDITOR_MODULE_WIDGET``)."""
    return text_rules(import_class(settings.XPREZ_CK_EDITOR_MODULE_WIDGET)())


def editor_config(widget):
    """The widget's CKEditor config, without file upload: its URL is set per
    admin, and uploading through the editor is not available over MCP."""
    try:
        config = widget.get_config()
    except (ValueError, NoReverseMatch):
        if not isinstance(widget, CkEditorFileUploadWidgetMixin):
            raise
        config = super(CkEditorFileUploadWidgetMixin, widget).get_config()
        if isinstance(widget, CkEditorTableMixin):  # before upload in the MRO
            config["toolbar"] = tuple(config.get("toolbar", ())) + ("insertTable",)
    for key in ("toolbar", "blockToolbar"):
        config[key] = tuple(
            item for item in config.get(key, ()) if item != "imageUpload"
        )
    return config


def _unique(values):
    return list(dict.fromkeys(values))
