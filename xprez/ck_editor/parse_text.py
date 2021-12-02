import sys
import urllib

from bs4 import BeautifulSoup
from django.template import Context, Template
from django.utils.safestring import mark_safe
from PIL import Image

try:
    import cStringIO
except ImportError:
    import io


def parse_text(text_source, request):
    if not text_source:
        return ''
    soup = BeautifulSoup(text_source, 'html5lib')

    # extract empty p elements from end of text
    for last_p in reversed(soup.find_all('p')):
        if last_p.text:
            break
        else:
            last_p.extract()

    for tag in soup.find_all('figure', attrs={'class': 'image'}):

        tag_img = tag.find('img')
        if tag_img:
            url = tag_img.get('src')

            if not url.lower().startswith('http') and request:
                url = request.build_absolute_uri(url)

            if sys.version_info >= (3, 0):
                file = io.BytesIO(urllib.request.urlopen(url).read())
            else:
                file = cStringIO.StringIO(urllib.urlopen(url).read())
            im = Image.open(file)
            width, height = im.size
            if 'image-style-align-right' in tag['class']:
                align = 'right'
            elif 'image-style-align-left' in tag['class']:
                align = 'left'
            else:
                align = 'center'

            caption_tag = tag.find('figcaption')
            if caption_tag:
                caption = caption_tag.text
            else:
                caption = ''

            alt_text = tag_img.get('alt', '')

            tag_link = tag.find('a')
            if tag_link:
                link_url = tag_link.get('href')
                link_new_window = tag_link.get('target') == '_blank'
            else:
                link_url = ""
                link_new_window = False

            tag.replaceWith('{%% ckeditor_content_image "%s" "%s" %s %s caption="%s" alt_text="%s" link_url="%s" link_new_window=%s %%}' % (
                url, align, width, height, caption, alt_text, link_url,
                'True' if link_new_window else 'False',
            ))

    for tag in soup.find_all(attrs={'contenteditable': True}):
        del tag['contenteditable']

    if sys.version_info >= (3, 0):
        text_parsed = str(soup)
    else:
        text_parsed = unicode(soup)
    return text_parsed


def render_text_parsed(text_parsed, extra_context={}):
    t = Template('{% load xprez %}' + text_parsed)
    c = Context({})
    c.update(extra_context)
    return mark_safe(t.render(c))
