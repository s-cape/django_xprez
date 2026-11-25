"""The HTML a rich text field accepts over MCP, derived from its CKEditor config.

Each toolbar item stands for the markup it produces, so the rules follow the
editor's config (``XPREZ_CK_EDITOR_*_CONFIG`` and the widget's mixins): what
an editor cannot produce in the admin, an MCP client cannot send either.
"""

from dataclasses import dataclass, field
from urllib.parse import urlsplit

from bs4 import BeautifulSoup, CData, Comment, Declaration, Doctype
from bs4 import NavigableString, ProcessingInstruction
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


# removed with their content: never page text
DROP_WITH_CONTENT = frozenset(
    {
        "script",
        "style",
        "iframe",
        "object",
        "embed",
        "template",
        "noscript",
        "svg",
        "math",
        "head",
        "title",
        "meta",
        "link",
        "form",
        "input",
        "button",
        "select",
        "textarea",
    }
)
BLOCK_TAGS = frozenset(
    {"p", "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "blockquote"}
    | {"figure", "table", "hr", "pre", "div"}
)
URL_SCHEMES = ("http", "https", "mailto", "tel")
TAG_ALIASES = {"b": "strong", "i": "em"}
HEADINGS = ("h1", "h2", "h3", "h4", "h5", "h6")
URL_ATTRIBUTES = frozenset({"href", "src"})
_SPECIAL = (Comment, CData, Declaration, Doctype, ProcessingInstruction)


def clean_html(value, rules):
    """``(html, notes)``: ``value`` reduced to what ``rules`` allow, and what
    was removed, for the client to know its text changed."""
    # parsed as xprez.ck_editor.parse_text does, the way browsers parse HTML
    soup = BeautifulSoup(value or "", "html5lib")
    body = soup.body
    # what the parser moved to <head> (a leading <script>, <title>) is dropped
    removed_head = {tag.name for tag in soup.head.find_all(True)}
    removed_tags, removed_attributes, renamed_tags = removed_head, set(), set()
    for node in body.find_all(string=lambda text: isinstance(text, _SPECIAL)):
        node.extract()
    for tag in body.find_all(True):
        if tag.decomposed:
            continue
        if tag.name in DROP_WITH_CONTENT:
            removed_tags.add(tag.name)
            tag.decompose()
        elif tag.name not in rules.tags and _rename(tag, rules, renamed_tags):
            removed_attributes |= _clean_attributes(tag, rules)
        elif tag.name not in rules.tags:
            removed_tags.add(tag.name)
            tag.unwrap()
        else:
            removed_attributes |= _clean_attributes(tag, rules)
    _wrap_top_level(soup, body)
    notes = []
    if renamed_tags:
        notes.append(f"changed tags: {', '.join(sorted(renamed_tags))}")
    if removed_tags:
        notes.append(f"removed tags: {', '.join(sorted(removed_tags))}")
    if removed_attributes:
        notes.append(f"removed attributes: {', '.join(sorted(removed_attributes))}")
    return body.decode_contents().strip(), notes


def _rename(tag, rules, renamed):
    """Give ``tag`` the allowed name with the same meaning, if there is one:
    ``b`` / ``i`` as ``strong`` / ``em``, a heading as the nearest allowed
    level (``h1`` as ``h2`` when the editor starts at ``h2``)."""
    name = TAG_ALIASES.get(tag.name)
    if name is None and tag.name in HEADINGS:
        allowed = [heading for heading in HEADINGS if heading in rules.tags]
        if allowed:
            level = HEADINGS.index(tag.name)
            name = min(
                allowed, key=lambda heading: abs(HEADINGS.index(heading) - level)
            )
    if name is None or name not in rules.tags:
        return False
    renamed.add(f"{tag.name} to {name}")
    tag.name = name
    return True


def _clean_attributes(tag, rules):
    removed = set()
    allowed = set(rules.attributes.get(tag.name, ()))
    classes = rules.classes.get(tag.name, ())
    for name in list(tag.attrs):
        value = tag.attrs[name]
        if name == "class":
            kept = [item for item in value if item in classes]
            if kept:
                tag.attrs["class"] = kept
                if len(kept) < len(value):
                    removed.add(f"{tag.name}.class")
            else:
                del tag.attrs["class"]
                removed.add(f"{tag.name}.class")
        elif name not in allowed:
            del tag.attrs[name]
            removed.add(f"{tag.name}.{name}")
        elif name in URL_ATTRIBUTES and not _safe_url(value):
            del tag.attrs[name]
            removed.add(f"{tag.name}.{name}")
        elif name == "target" and value != "_blank":
            del tag.attrs[name]
            removed.add(f"{tag.name}.{name}")
    return removed


def _safe_url(value):
    # browsers ignore control characters and whitespace inside the scheme
    url = "".join(char for char in str(value) if ord(char) > 32).strip()
    scheme = urlsplit(url).scheme.lower()
    return not scheme or scheme in URL_SCHEMES


def _wrap_top_level(soup, body):
    """Wrap top-level text and inline tags in ``<p>``, as the editor does."""
    paragraph = None
    for node in list(body.contents):
        is_block = getattr(node, "name", None) in BLOCK_TAGS
        is_blank = isinstance(node, NavigableString) and not node.strip()
        if is_block:
            paragraph = None
        elif is_blank and paragraph is None:
            continue
        else:
            if paragraph is None:
                paragraph = soup.new_tag("p")
                node.insert_before(paragraph)
            paragraph.append(node.extract())
