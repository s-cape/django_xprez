from django import template

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


@register.filter
def xprez_file_thumbnail(value, size="200x200"):
    """Try to generate a sorl-thumbnail for value; return thumb or None on failure."""
    if not value:
        return None
    try:
        from sorl.thumbnail import get_thumbnail

        return get_thumbnail(value, size, format="WEBP", quality=80)
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
