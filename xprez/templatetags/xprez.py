# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import template
from django.forms import Media

from .. import module_manager, settings
from ..utils import build_absolute_uri as _build_absolute_uri

register = template.Library()


class PrefixableMedia(Media):
    @staticmethod
    def from_media(media):
        prefixable = PrefixableMedia()
        prefixable._css_lists = media._css_lists
        prefixable._js_lists = media._js_lists
        return prefixable

    def absolute_path(self, path):
        absolute_path = super().absolute_path(path)
        if settings.XPREZ_USE_ABSOLUTE_URI and not path.startswith(
            ("http://", "https://", "//")
        ):
            return "{}{}".format(settings.XPREZ_BASE_URL, absolute_path)
        else:
            return absolute_path


@register.simple_tag()
def xprez_front_media(modules=None):
    """
    Returns the media required by the modules.
    If modules is None, returns the media required by all modules.
    """
    if modules is None:
        modules = None
    else:
        modules = {module.content_type for module in modules}

    return str(PrefixableMedia.from_media(module_manager.front_media(modules=modules)))


@register.simple_tag(takes_context=True)
def xprez_container_render_front(context, container):
    return container.render_front(context.flatten())


@register.simple_tag(takes_context=True)
def xprez_section_render_front(context, section):
    return section.render_front(context.flatten())


@register.simple_tag(takes_context=True)
def xprez_module_render_front(context, module):
    return module.polymorph().render_front(context.flatten())


@register.inclusion_tag("xprez/includes/medium_image.html", takes_context=True)
def medium_module_image(context, url, align, width, height, caption=None):
    return _editor_module_image(context, url, align, width, height, caption=caption)


@register.inclusion_tag("xprez/includes/ckeditor_image.html", takes_context=True)
def ckeditor_module_image(
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
