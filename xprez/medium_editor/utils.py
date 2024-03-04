import io
import urllib

from bs4 import BeautifulSoup
from django.template import Context, Template
from django.utils.safestring import mark_safe
from PIL import Image


def parse_text(text_source):
    if not text_source:
        return ""
    soup = BeautifulSoup(text_source, "html5lib")

    # extract empty p elements from end of text
    for last_p in reversed(soup.find_all("p")):
        if last_p.text:
            break
        else:
            last_p.extract()

    for tag in soup.find_all("div", attrs={"class": "medium-insert-images"}):
        tag_img = tag.find("img")
        if tag_img:
            url = tag_img.get("src")

            request = urllib.request.Request(
                url, headers={"User-agent": ""}  # needed for cloudflare
            )

            file = io.BytesIO(urllib.request.urlopen(request).read())
            im = Image.open(file)
            width, height = im.size
            if "medium-insert-images-right" in tag["class"]:
                align = "right"
            elif "medium-insert-images-left" in tag["class"]:
                align = "left"
            else:
                align = "center"

            caption_tag = tag.find("figcaption")
            if caption_tag:
                caption = caption_tag.text
            else:
                caption = ""

            tag.replaceWith(
                '{%% medium_content_image "%s" "%s" %s %s "%s" %%}'
                % (url, align, width, height, caption)
            )

    for tag in soup.find_all(attrs={"contenteditable": True}):
        del tag["contenteditable"]

    text_parsed = str(soup)
    return text_parsed


def render_text_parsed(text_parsed, extra_context={}):
    t = Template("{% load xprez %}" + text_parsed)
    c = Context({})
    c.update(extra_context)
    return mark_safe(t.render(c))
