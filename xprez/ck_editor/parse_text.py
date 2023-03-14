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


def _replace_wrapper_with_templatetag(wrapper, img, request):
    # wrapper and img may be the same tag - that is the case of inline images
    src = img.get("src")

    if not src.lower().startswith("http") and request:
        src = request.build_absolute_uri(src)

    if sys.version_info >= (3, 0):
        file = io.BytesIO(urllib.request.urlopen(src).read())
    else:
        file = cStringIO.StringIO(urllib.urlopen(src).read())
    im = Image.open(file)
    width, height = im.size
    classes = list(img.get("class", [])) + list(wrapper.get("class", []))
    if "image-style-align-right" in classes:
        align = "right"
    elif "image-style-align-left" in classes:
        align = "left"
    else:
        align = "center"

    caption_tag = wrapper.find("figcaption")
    if caption_tag:
        caption = caption_tag.text
    else:
        caption = ""

    alt_text = img.get("alt", "")

    tag_link = wrapper.find("a")
    if tag_link:
        link_url = tag_link.get("href")
        link_new_window = tag_link.get("target") == "_blank"
    else:
        link_url = ""
        link_new_window = False

    wrapper.replaceWith(
        '{%% ckeditor_content_image "%s" "%s" %s %s caption="%s" alt_text="%s" link_url="%s" link_new_window=%s %%}'
        % (
            src,
            align,
            width,
            height,
            caption,
            alt_text,
            link_url,
            "True" if link_new_window else "False",
        )
    )


def parse_text(text_source, request):
    if not text_source:
        return ""
    soup = BeautifulSoup(text_source, "html5lib")

    # extract empty p elements from end of text
    for last_p in reversed(soup.find_all("p")):
        if last_p.text:
            break
        else:
            last_p.extract()

    for wrapper in soup.find_all("figure", attrs={"class": "image"}):
        img = wrapper.find("img")
        if img:
            _replace_wrapper_with_templatetag(wrapper, img, request)

    inline_images = []
    inline_images += soup.find_all("img", attrs={"class": "image-style-align-left"})
    inline_images += soup.find_all("img", attrs={"class": "image-style-align-right"})
    for img in inline_images:
        _replace_wrapper_with_templatetag(img, img, request)

    for tag in soup.find_all(attrs={"contenteditable": True}):
        del tag["contenteditable"]

    return str(soup)


def render_text_parsed(text_parsed, extra_context={}):
    t = Template("{% load xprez %}" + text_parsed)
    c = Context({})
    c.update(extra_context)
    return mark_safe(t.render(c))
