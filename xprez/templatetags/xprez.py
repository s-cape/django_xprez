from django import template

from ..media import FrontendMediaCollector
from ..models.mixins.responsive_image import InlineResponsiveImage
from ..utils import build_absolute_uri as _build_absolute_uri

register = template.Library()


@register.simple_tag()
def xprez_front_media(container=None):
    return str(FrontendMediaCollector(container=container).get_media())


@register.simple_tag(takes_context=True)
def xprez_container_render_front(context, container):
    return container.render_front_cached(context.flatten())


@register.simple_tag(takes_context=True)
def xprez_section_render_front(context, section):
    return section.render_front_cached(context.flatten())


@register.simple_tag(takes_context=True)
def xprez_module_render_front(context, module):
    return module.polymorph.render_front_cached(context.flatten())


@register.inclusion_tag("xprez/includes/ckeditor_image.html", takes_context=True)
def ckeditor_image(
    context,
    url,
    align,
    caption=None,
    alt_text=None,
    link_url="",
    link_new_window=False,
):
    image = InlineResponsiveImage(url, parent_module=context.get("module"))
    return {
        "image": image,
        "url": _build_absolute_uri(url),
        "align": align,
        "caption": caption,
        "alt_text": alt_text,
        "link_url": link_url,
        "link_new_window": link_new_window,
    }


@register.filter()
def build_absolute_uri(url):
    return _build_absolute_uri(url)
