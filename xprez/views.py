from django.http import HttpResponse

from xprez import module_registry
from xprez.conf import settings
from xprez.models import ConfigParentMixin, Module, Section


def variables_css(request):
    # TODO: move most of the code to models/css.py
    result = []
    breakpoints = list(settings.XPREZ_BREAKPOINTS.keys())

    # Section CSS - BP0
    section = Section()
    section_current_css = section.get_css()
    section_current_css.update(section.build_config(0).get_css())
    result += [
        ConfigParentMixin._format_css_rule(".xprez-section", 0, section_current_css)
    ]

    # Section CSS - BP1+
    for breakpoint in breakpoints[1:]:
        config = Section().build_config(breakpoint)
        config.css_breakpoint = breakpoint
        css = config.get_css()
        changed = ConfigParentMixin._diff_css(section_current_css, css)
        if changed:
            result += [
                ConfigParentMixin._format_css_rule(
                    ".xprez-section", breakpoint, changed
                )
            ]
        section_current_css.update(css)

    # Default module CSS - BP0
    module_current_css = Module().build_config(0).get_css()
    result += [
        ConfigParentMixin._format_css_rule(".xprez-module", 0, module_current_css)
    ]

    # Default module CSS - BP1+
    for breakpoint in breakpoints[1:]:
        config = Module().build_config(breakpoint)
        config.css_breakpoint = breakpoint
        css = config.get_css()
        changed = ConfigParentMixin._diff_css(module_current_css, css)
        if changed:
            result += [
                ConfigParentMixin._format_css_rule(".xprez-module", breakpoint, changed)
            ]
        module_current_css.update(css)

    # Specific module CSS
    for module_class in module_registry._registry.values():
        # BP0: Diff specific module vs default module
        default_module_css = Module().build_config(0).get_css()
        config = module_class().build_config(0)
        config.css_breakpoint = 0
        specific_current_css = config.get_css()

        changed = module_class._diff_css(default_module_css, specific_current_css)
        if changed:
            result += [
                ConfigParentMixin._format_css_rule(
                    f".xprez-module.{module_class.module_css_class()}", 0, changed
                )
            ]

        # BP1+: Diff against previous breakpoint of same module
        for breakpoint in breakpoints[1:]:
            config = module_class().build_config(breakpoint)
            config.css_breakpoint = breakpoint
            specific_css = config.get_css()

            changed = module_class._diff_css(specific_current_css, specific_css)
            if changed:
                result += [
                    ConfigParentMixin._format_css_rule(
                        f".xprez-module.{module_class.module_css_class()}",
                        breakpoint,
                        changed,
                    )
                ]
            specific_current_css.update(specific_css)

    return HttpResponse("\n".join(result), content_type="text/css")
