"""The editing guide served by ``xprez_guide`` and ``xprez://guide/{topic}``.

The texts are bundled in ``guide/``. A project overrides a topic with a
template ``xprez/mcp/guide/<topic>.md``, which gets the same context.
"""

import html
from pathlib import Path

from django.template import Context, Template, TemplateDoesNotExist
from django.template.loader import get_template

from xprez import module_registry
from xprez.conf import settings

from .html import module_text_rules

GUIDE_DIR = Path(__file__).parent / "guide"

TOPICS = {
    "index": "How content is structured, and where to start.",
    "editing": "Changes are live: how to edit safely, best practices.",
    "layout": "Sections, columns and breakpoints.",
    "modules": "What each module is for.",
    "text": "The HTML text fields accept.",
}

# Custom modules describe themselves with an ``mcp_summary`` attribute.
MODULE_SUMMARIES = {
    "xprez.TextModule": "Rich text, optionally with one image or video.",
    "xprez.QuoteModule": "A quotation with the name of who said it, optionally a photo.",
    "xprez.GalleryModule": "One or more images in a grid, optionally with a lightbox.",
    "xprez.FilesModule": "Files for visitors to download.",
    "xprez.VideoModule": "An embedded video, given by its URL.",
    "xprez.NumbersModule": "Key figures, each with a short caption.",
    "xprez.AccordionModule": "Expandable items, such as questions and answers.",
    "xprez.CodeInputModule": "Raw code inserted into the page; for developers.",
    "xprez.CodeTemplateModule": "A predefined template from the project's code.",
    "xprez.AnchorModule": "A target for in-page links.",
    "xprez.ModuleSymlink": "A module shown from another page.",
}


def render_topic(topic):
    if topic not in TOPICS:
        raise LookupError(topic)
    context = guide_context()
    try:
        return get_template(f"xprez/mcp/guide/{topic}.md").render(context)
    except TemplateDoesNotExist:
        source = (GUIDE_DIR / f"{topic}.md").read_text(encoding="utf-8")
        return Template(source).render(Context(context))


def guide_context():
    return {
        "topics": [
            {"name": name, "summary": summary} for name, summary in TOPICS.items()
        ],
        "breakpoints": [
            (number, {"name": breakpoint_name(number)})
            for number in settings.XPREZ_BREAKPOINTS
        ],
        "text_rules": module_text_rules(),
        "modules": [
            {
                "type": module_class.module_key,
                "name": module_class._meta.verbose_name,
                "summary": module_summary(module_class),
            }
            for module_class in module_registry.allowed_module_classes()
        ],
    }


def breakpoint_name(number):
    # the defaults are written for HTML (``&lt;``)
    return html.unescape(str(settings.XPREZ_BREAKPOINTS[number]["name"]))


def module_summary(module_class):
    summary = getattr(module_class, "mcp_summary", None)
    if summary is None:
        summary = MODULE_SUMMARIES.get(module_class.class_content_type())
    return summary
