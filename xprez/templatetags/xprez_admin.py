from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def xprez_content_render_admin(context, content):
    return content.render_admin(context.flatten())


@register.simple_tag(takes_context=True)
def xprez_section_render_admin(context, section):
    return section.render_admin(context.flatten())


@register.simple_tag(takes_context=True)
def xprez_section_config_render_admin(context, config):
    return config.render_admin(context.flatten())


@register.simple_tag(takes_context=True)
def xprez_content_config_render_admin(context, config):
    return config.render_admin(context.flatten())


@register.simple_tag()
def xprez_clipboard_is_empty(xprez_admin, request):
    return xprez_admin.xprez_clipboard_is_empty(request)
