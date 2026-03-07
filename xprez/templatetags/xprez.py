# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import template

from ..media import FrontendMediaCollector
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
    width,
    height,
    caption=None,
    alt_text=None,
    link_url="",
    link_new_window=False,
):
    return _editor_module_image(
        context,
        url,
        align,
        width,
        height,
        caption=caption,
        alt_text=alt_text,
        link_url=link_url,
        link_new_window=link_new_window,
    )


def _editor_module_image(
    context,
    url,
    align,
    width,
    height,
    caption=None,
    alt_text=None,
    link_url="",
    link_new_window=False,
):
    MAX_SIZE = {
        "center": (1000, 1000),
        "left": (450, 450),
        "right": (450, 450),
    }

    LIGHTBOX_THRESHOLD_SIZE = {
        "center": (1200, 1200),
        "left": (550, 550),
        "right": (550, 550),
    }

    threshold_size = {
        "width": LIGHTBOX_THRESHOLD_SIZE[align][0],
        "height": LIGHTBOX_THRESHOLD_SIZE[align][1],
    }
    max_size = {"width": MAX_SIZE[align][0], "height": MAX_SIZE[align][1]}

    lightbox = threshold_size["width"] < width or threshold_size["height"] < height

    image_context = {
        "url": _build_absolute_uri(url),
        "align": align,
        "width": width,
        "height": height,
        "lightbox": lightbox,
        "max_size": "%sx%s" % (max_size["width"], max_size["height"]),
        "link_url": link_url,
        "link_new_window": link_new_window,
        "caption": caption,
        "alt_text": alt_text,
    }

    return image_context


@register.filter()
def build_absolute_uri(url):
    return _build_absolute_uri(url)
