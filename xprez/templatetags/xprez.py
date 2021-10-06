# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import warnings

from django import template

from .. import contents_manager
from ..settings import XPREZ_BASE_URL, XPREZ_USE_ABSOLUTE_URI
from ..utils import build_absolute_uri as build_abs_uri

register = template.Library()


@register.inclusion_tag('xprez/includes/media.html')
def xprez_front_media():
    return {
        'BASE_URL': XPREZ_BASE_URL,
        'USE_ABSOLUTE_URI': XPREZ_USE_ABSOLUTE_URI,
        'contents_media': contents_manager.front_media(),
    }


@register.simple_tag(takes_context=True)
def xprez_content_render_front(context, content):
    polymorph = content.polymorph()
    try:
        return polymorph.render_front(extra_context=context.flatten())
    except TypeError:
        warnings.warn("Deprecation warning: {} render_front() should accept context attribute.".format(type(polymorph)), DeprecationWarning)
        return polymorph.render_front()


@register.inclusion_tag('xprez/includes/medium_image.html', takes_context=True)
def medium_content_image(context, url, align, width, height, caption=None):
    return _editor_content_image(context, url, align, width, height, caption=caption)


@register.inclusion_tag('xprez/includes/ckeditor_image.html', takes_context=True)
def ckeditor_content_image(context, url, align, width, height, caption=None, alt_text=None, link_url='', link_new_window=False):
    return _editor_content_image(context, url, align, width, height, caption=caption, alt_text=alt_text, link_url=link_url, link_new_window=link_new_window)


def _editor_content_image(context, url, align, width, height, caption=None, alt_text=None, link_url='', link_new_window=False):
    MAX_SIZE = {
        'center': (1000, 1000),
        'left': (450, 450),
        'right': (450, 450),
    }

    LIGHTBOX_THRESHOLD_SIZE = {
        'center': (1200, 1200),
        'left': (550, 550),
        'right': (550, 550),
    }

    threshold_size = {'width': LIGHTBOX_THRESHOLD_SIZE[align][0], 'height': LIGHTBOX_THRESHOLD_SIZE[align][1]}
    max_size = {'width': MAX_SIZE[align][0], 'height': MAX_SIZE[align][1]}

    lightbox = threshold_size['width'] < width or threshold_size['height'] < height

    image_context = {
        'url': build_abs_uri(url),
        'align': align,
        'width': width,
        'height': height,
        'lightbox': lightbox,
        'max_size': '%sx%s' % (max_size['width'], max_size['height']),
        'link_url': link_url,
        'link_new_window': link_new_window,
        'caption': caption,
        'alt_text': alt_text,
    }

    return image_context


@register.filter()
def build_absolute_uri(url):
    return build_abs_uri(url)
