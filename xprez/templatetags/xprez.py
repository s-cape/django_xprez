# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django import template
from .. import contents_manager
register = template.Library()


@register.inclusion_tag('xprez/includes/media.html')
def xprez_front_media():
    return {
        'contents_media': contents_manager.front_media(),
    }


@register.inclusion_tag('xprez/includes/medium_image.html', takes_context=True)
def medium_content_image(context, url, align, width, height, caption=None):
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
        'url': url,
        'align': align,
        'width': width,
        'height': height,
        'lightbox': lightbox,
        'max_size': '%sx%s' % (max_size['width'], max_size['height']),
        'caption': caption,
    }

    return image_context
