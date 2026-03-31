from pathlib import Path

from django import template
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from PIL import Image
from sorl.thumbnail import get_thumbnail

register = template.Library()


@register.simple_tag(takes_context=True)
def xprez_module_render_admin(context, module):
    return module.render_admin(context.flatten())


@register.simple_tag(takes_context=True)
def xprez_section_render_admin(context, section):
    return section.render_admin(context.flatten())


@register.simple_tag(takes_context=True)
def xprez_section_config_render_admin(context, config):
    return config.render_admin(context.flatten())


@register.simple_tag(takes_context=True)
def xprez_module_config_render_admin(context, config):
    return config.render_admin(context.flatten())


@register.simple_tag()
def xprez_clipboard_is_empty(xprez_admin, request):
    return xprez_admin.xprez_clipboard_is_empty(request)


@register.simple_tag()
def xprez_admin_change_url(xprez_admin, obj):
    try:
        return reverse(
            "{namespace}:{app_label}_{model_name}_change".format(
                namespace=xprez_admin.xprez_url_namespace,
                app_label=obj._meta.app_label,
                model_name=obj._meta.model_name,
            ),
            args=[obj.pk],
        )
    except NoReverseMatch:
        return None


@register.filter
def xprez_file_name(value):
    """Return the filename (no directory path) for a file field value."""
    name = getattr(value, "name", None) or str(value)
    return Path(name).name


@register.filter
def xprez_file_thumbnail(value, size="400x200"):
    """Try to generate a sorl-thumbnail for value; return thumb or None on failure."""
    if not value:
        return None
    try:
        with value.open("rb") as f:
            Image.open(f)  # check if file is an image
        return get_thumbnail(value, size, format="WEBP", quality=80) or None
    except Exception:
        return None


@register.filter
def xprez_widget_context(field):
    """Return widget context dict for the field's widget (or None)."""
    attrs = field.build_widget_attrs({})
    context = field.field.widget.get_context(field.html_name, field.value(), attrs)
    widget = context.get("widget")
    if widget is None:
        return None
    if widget.get("attrs") is None:
        widget = {**widget, "attrs": {}}
    return widget
