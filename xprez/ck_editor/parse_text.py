from bs4 import BeautifulSoup, NavigableString, Tag
from django.template import Context, Template
from django.utils.safestring import mark_safe


def parse_text(text_source):
    if not text_source:
        return ""
    soup = BeautifulSoup(text_source, "html5lib")

    _remove_trailing_empty_br_and_p(soup)

    for wrapper in soup.find_all("figure", attrs={"class": "image"}):
        img = wrapper.find("img")
        if img:
            _replace_wrapper_with_templatetag(wrapper, img)

    inline_images = soup.find_all(
        "img", attrs={"class": "image-style-align-left"}
    ) + soup.find_all("img", attrs={"class": "image-style-align-right"})
    for img in inline_images:
        _replace_wrapper_with_templatetag(img, img)

    # Catch-all: plain <img> tags not wrapped in a figure and without alignment classes
    for img in soup.find_all("img"):
        _replace_wrapper_with_templatetag(img, img)

    for tag in soup.find_all(attrs={"contenteditable": True}):
        del tag["contenteditable"]

    return soup.body.decode_contents()


def render_text_parsed(text_parsed, extra_context=None):
    t = Template("{% load xprez %}" + text_parsed)
    c = Context({})
    if extra_context:
        c.update(extra_context)
    return mark_safe(t.render(c))


def _remove_trailing_empty_br_and_p(soup):
    body = soup.body
    if not body:
        return

    while body.contents:
        trailing_node = body.contents[-1]
        if not _is_empty_node(trailing_node):
            break
        trailing_node.extract()


def _is_empty_node(node):
    if isinstance(node, NavigableString):
        return _is_blank_string(str(node))
    elif isinstance(node, Tag):
        return _is_empty_br_or_p(node)
    else:
        return False


def _is_empty_br_or_p(tag):
    return (
        not tag.attrs
        and tag.name in ("br", "p")
        and _is_blank_string(tag.get_text())
        and all(_is_bare_br(child) for child in tag.find_all(True))
    )


def _is_bare_br(tag):
    return tag.name == "br" and not tag.attrs


def _is_blank_string(value):
    return not value.replace("\xa0", " ").strip()


def _replace_wrapper_with_templatetag(wrapper, img):
    # wrapper and img may be the same tag (inline images)
    src = img.get("src")
    if not src:
        wrapper.extract()
        return

    classes = list(img.get("class", [])) + list(wrapper.get("class", []))
    if "image-style-align-right" in classes:
        align = "right"
    elif "image-style-align-left" in classes:
        align = "left"
    else:
        align = "center"

    caption_tag = wrapper.find("figcaption")
    caption = caption_tag.text if caption_tag else ""

    alt_text = img.get("alt", "")

    link_tag = wrapper.find("a")
    link_url = link_tag.get("href") if link_tag else ""
    link_new_window = bool(link_tag and link_tag.get("target") == "_blank")

    wrapper.replaceWith(
        f'{{% ckeditor_image "{src}" "{align}"'
        f' caption="{caption}" alt_text="{alt_text}"'
        f' link_url="{link_url}" link_new_window={link_new_window} %}}'
    )
