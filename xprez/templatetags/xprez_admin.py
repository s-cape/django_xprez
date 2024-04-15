from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def xprez_content_render_admin(context, content):
    return content.render_admin(context.flatten())


@register.simple_tag(takes_context=True)
def get_xprez_clipboard(context, xprez_admin, request, container):
    return context.get(
        "xprez_clipboard", xprez_admin.xprez_clipboard_list(request, container)
    )
