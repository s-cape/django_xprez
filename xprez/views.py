from django.http import HttpResponse

from xprez import module_registry
from xprez.conf import settings
from xprez.models import ConfigParentMixin, Module, Section


def variables_css(request):
    result = []

    section_css = Section().build_config(settings.XPREZ_DEFAULT_BREAKPOINT).get_css()
    result += [
        ConfigParentMixin._get_breakpoint_css(
            ".xprez-section", settings.XPREZ_DEFAULT_BREAKPOINT, section_css
        )
    ]

    default_module_css = (
        Module().build_config(settings.XPREZ_DEFAULT_BREAKPOINT).get_css()
    )
    result += [
        ConfigParentMixin._get_breakpoint_css(
            ".xprez-module", settings.XPREZ_DEFAULT_BREAKPOINT, default_module_css
        )
    ]
    for module_class in module_registry._registry.values():
        module_css = module_class._get_changed_css(
            default_module_css,
            module_class().build_config(settings.XPREZ_DEFAULT_BREAKPOINT).get_css(),
        )
        if module_css:
            result += [
                ConfigParentMixin._get_breakpoint_css(
                    f".xprez-module.{module_class.module_css_class()}",
                    settings.XPREZ_DEFAULT_BREAKPOINT,
                    module_css,
                )
            ]

    return HttpResponse("\n".join(result), content_type="text/css")
