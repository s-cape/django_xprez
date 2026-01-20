from django.http import HttpResponse

from xprez import module_registry
from xprez.conf import settings
from xprez.models import ConfigParentMixin, Module, Section


def variables_css(request):
    result = []

    for breakpoint in settings.XPREZ_BREAKPOINTS:
        section_css = Section().build_config(breakpoint).get_css()
        result += [
            ConfigParentMixin._format_css_rule(
                ".xprez-section", breakpoint, section_css
            )
        ]

        default_module_css = Module().build_config(breakpoint).get_css()
        result += [
            ConfigParentMixin._format_css_rule(
                ".xprez-module", breakpoint, default_module_css
            )
        ]

        for module_class in module_registry._registry.values():
            module_css = module_class._diff_css(
                default_module_css,
                module_class().build_config(breakpoint).get_css(),
            )
            if module_css:
                result += [
                    ConfigParentMixin._format_css_rule(
                        f".xprez-module.{module_class.module_css_class()}",
                        breakpoint,
                        module_css,
                    )
                ]

    return HttpResponse("\n".join(result), content_type="text/css")
