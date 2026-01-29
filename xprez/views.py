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
    section_current_css_variables = section.get_css_variables()
    section_current_css_variables.update(section.build_config(0).get_css_variables())
    result += [
        ConfigParentMixin._format_css_rule(
            ".xprez-section", 0, section_current_css_variables
        )
    ]

    # Section CSS - BP1+
    for breakpoint in breakpoints[1:]:
        config = Section().build_config(breakpoint)
        config.css_breakpoint = breakpoint
        css = config.get_css_variables()
        changed_css_variables = ConfigParentMixin._diff_css_variables(
            section_current_css_variables, css
        )
        if changed_css_variables:
            result += [
                ConfigParentMixin._format_css_rule(
                    ".xprez-section", breakpoint, changed_css_variables
                )
            ]
        section_current_css_variables.update(css)

    # Default module CSS - BP0
    module_current_css_variables = Module().build_config(0).get_css_variables()
    result += [
        ConfigParentMixin._format_css_rule(
            ".xprez-module", 0, module_current_css_variables
        )
    ]

    # Default module CSS - BP1+
    for breakpoint in breakpoints[1:]:
        config = Module().build_config(breakpoint)
        config.css_breakpoint = breakpoint
        css = config.get_css_variables()
        changed_css_variables = ConfigParentMixin._diff_css_variables(
            module_current_css_variables, css
        )
        if changed_css_variables:
            result += [
                ConfigParentMixin._format_css_rule(
                    ".xprez-module", breakpoint, changed_css_variables
                )
            ]
        module_current_css_variables.update(css)

    # Specific module CSS
    for module_class in module_registry._registry.values():
        # BP0: Diff specific module vs default module
        default_module_css_variables = Module().build_config(0).get_css_variables()
        config = module_class().build_config(0)
        config.css_breakpoint = 0
        specific_current_css_variables = config.get_css_variables()

        changed_css_variables = module_class._diff_css_variables(
            default_module_css_variables, specific_current_css_variables
        )
        if changed_css_variables:
            result += [
                ConfigParentMixin._format_css_rule(
                    f".{module_class.module_css_class()}", 0, changed_css_variables
                )
            ]

        # BP1+: Diff against previous breakpoint of same module
        for breakpoint in breakpoints[1:]:
            config = module_class().build_config(breakpoint)
            config.css_breakpoint = breakpoint
            specific_css_variables = config.get_css_variables()

            changed_css_variables = module_class._diff_css_variables(
                specific_current_css_variables, specific_css_variables
            )
            if changed_css_variables:
                result += [
                    ConfigParentMixin._format_css_rule(
                        f".{module_class.module_css_class()}",
                        breakpoint,
                        changed_css_variables,
                    )
                ]
            specific_current_css_variables.update(specific_css_variables)

    return HttpResponse("\n".join(result), content_type="text/css")
