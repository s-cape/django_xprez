from xprez import constants
from xprez.conf import settings

"TODO: this file need cleanup"


def _get_unit_string(css_config, choice=None):
    """Extract unit string from config, handling dict or string units."""
    if not css_config:
        return ""
    units = css_config.get("units", "")
    if isinstance(units, dict):
        return units.get(choice, "") if choice else ""
    else:
        return units


class ChoiceUnitsProxy:
    """Proxy to access choice-specific units."""

    def __init__(self, css_config):
        self.css_config = css_config

    def __getattr__(self, choice):
        """
        Returns unit for specific choice: config.units.max_width.small -> 'px'
        """
        return _get_unit_string(self.css_config, choice)


class UnitsProxy:
    """Proxy to access units from XPREZ_CSS for any field."""

    def __init__(self, config):
        self.config = config

    def __getattr__(self, field_name):
        """
        Returns ChoiceUnitsProxy for any field.
        - Simple: config.units.padding_top.custom -> 'px'
        - Choice-specific: config.units.max_width.custom -> 'px'
        """
        css_config = self.config._get_css_config(field_name)
        return ChoiceUnitsProxy(css_config)


class CssMixin:
    """Base mixin for CSS generation from config fields."""

    def get_css_variables(self):
        return {}

    def get_css_classes(self):
        return {}

    def _get_choice_or_custom(self, field_prefix):
        """Get CSS value - transformed choice or formatted custom."""
        choice_value = getattr(self, f"{field_prefix}_choice")
        if choice_value == constants.CUSTOM:
            return self._format_css_value(
                self._get_css_config(field_prefix),
                self._get_value_or_default(f"{field_prefix}_custom"),
                choice_value,
            )
        else:
            return self._transform_css(field_prefix, choice_value)

    def _get_value_or_default(self, field_name):
        """Return value if non-empty, else resolve default for field_name."""
        value = getattr(self, field_name)
        if value not in [None, constants.NONE]:
            return value
        return self._lookup_by_config_keys(settings.XPREZ_DEFAULTS, field_name)

    def _transform_css(self, attr, value):
        """("margin_bottom", "small") -> "20px" """
        css_config = self._get_css_config(attr)
        breakpoints = css_config.get("values", {}).get(value) if css_config else None
        if not breakpoints:
            return value
        raw = self._resolve_breakpoint(breakpoints)
        return self._format_css_value(css_config, raw, value)

    def _get_css_config(self, attr):
        """Get XPREZ_CSS config for attr, with fallback to default."""
        result = self._lookup_by_config_keys(settings.XPREZ_CSS, attr)
        if result:
            return result
        return settings.XPREZ_CSS.get("default", {}).get(attr)

    def _lookup_by_config_keys(self, source, field_name):
        """Lookup field_name in source dict using get_css_config_keys() priority."""
        for key in self.get_css_config_keys():
            config = source
            for part in key.split("."):
                config = config.get(part, {})
            if field_name in config:
                return config[field_name]
        return None

    def _resolve_breakpoint(self, breakpoints):
        """Get value for current breakpoint, falling back to lower."""
        for bp in range(self.css_breakpoint, -1, -1):
            if bp in breakpoints:
                return breakpoints[bp]
        return None

    def _format_css_value(self, css_config, value, choice=None):
        """Apply units from config to value."""
        if value is None:
            return ""

        units = _get_unit_string(css_config, choice)
        return f"{value}{units}"

    @property
    def units(self):
        """Proxy for accessing units: config.units.margin_bottom"""
        return UnitsProxy(self)

    def get_css_config_keys(self):
        """Return keys for XPREZ_CSS lookup in priority order. Override in subclasses."""
        raise NotImplementedError()


class CssParentMixin(CssMixin):
    """
    Extends CssMixin with responsive CSS rendering for parent elements.

    Provides its own get_css_variables() AND aggregates get_css_variables() from child configs,
    merging them across breakpoints into a single <style> tag.
    """

    css_breakpoint = settings.XPREZ_DEFAULT_BREAKPOINT

    def get_css_variables(self):
        return {}

    def get_css_variables_by_breakpoint(self):
        """
        Compute changed css per breakpoint (compared to defaults).

        Returns: {0: {"columns": 2}, 2: {"columns": 3}}
        """
        db_configs = {c.css_breakpoint: c for c in self.get_configs()}
        current_css_variables = self.build_config(
            settings.XPREZ_DEFAULT_BREAKPOINT
        ).get_css_variables()
        result = {}
        last_config = None

        parent_css_variables = self.get_css_variables()
        if parent_css_variables:
            result[0] = parent_css_variables

        for breakpoint in settings.XPREZ_BREAKPOINTS:
            if breakpoint in db_configs:
                config = db_configs[breakpoint]
                last_config = config
            elif last_config:
                # Reuse last DB config with updated breakpoint for _transform_css
                last_config.css_breakpoint = breakpoint
                config = last_config
            else:
                config = self.build_config(breakpoint)

            css_variables = {
                **result.get(breakpoint, {}),  # parent_css - if present
                **self._diff_css_variables(
                    current_css_variables, config.get_css_variables()
                ),
            }
            result[breakpoint] = css_variables
            current_css_variables.update(css_variables)

        return result

    @staticmethod
    def _diff_css_variables(base_css_variables, css_variables):
        """
        Return only css that differs from base.

        ({"a": 1, "b": 2}, {"a": 1, "b": 3, "c": 4}) -> {"b": 3, "c": 4}
        """
        changed = {}
        for key, value in css_variables.items():
            if value != base_css_variables.get(key):
                changed[key] = value
        return changed

    @staticmethod
    def _format_css_variables(css_variables):
        """
        Convert dict to CSS variables string.

        {"columns": 2, "gap": "1rem"} -> "--x-columns: 2; --x-gap: 1rem"
        """
        result = []
        for k, v in css_variables.items():
            if v is not None:
                result += [f"--x-{k}: {v}"]
        return "; ".join(result)

    @staticmethod
    def _format_css_rule(selector, breakpoint, css_variables):
        """
        Wrap CSS vars in selector and media query (if breakpoint has min_width).

        ("#id", 0, {"a": 1}) -> "#id { --x-a: 1; }"
        ("#id", 2, {"a": 1}) -> "@media (min-width: 768px) { #id { --x-a: 1; } }"
        """
        if not css_variables:
            return ""

        css_variables_string = CssParentMixin._format_css_variables(css_variables)
        min_width = settings.XPREZ_BREAKPOINTS[breakpoint]["min_width"]
        rule = f"{selector} {{ {css_variables_string}; }}"
        if not min_width:
            return rule
        else:
            return f"@media (min-width: {min_width}px) {{ {rule} }}"

    def render_css_variables(self):
        """
        Generate <style> tag with all breakpoint styles.

        Returns: "<style>#section-config-1 { --x-columns: 1; }</style>"
        """
        css_data = self.get_css_variables_by_breakpoint()
        if not css_data:
            return ""

        selector = "#" + self.key
        output = []

        for breakpoint, css_variables in css_data.items():
            rule = self._format_css_rule(selector, breakpoint, css_variables)
            if rule:
                output += [rule]

        if output:
            return "<style>" + "".join(output) + "</style>"
        else:
            return ""

    def get_css_classes_by_breakpoint(self):
        """
        Compute changed CSS classes per breakpoint (compared to previous).

        Example for TextModule with font-size change at bp2:
        {0: {"background": True, "font-size": "normal"}, 2: {"font-size": "large"}}
        """
        configs = {c.css_breakpoint: c for c in self.get_configs()}
        current_css_classes = {}
        result = {}

        for breakpoint, config in configs.items():
            css_classes = self._diff_css_classes(
                current_css_classes, config.get_css_classes()
            )
            if css_classes:
                result[breakpoint] = css_classes
            current_css_classes.update(css_classes)

        return result

    @staticmethod
    def _diff_css_classes(existing_css_classes, css_classes):
        """
        Return only classes that differ from existing.

        >>> CssParentMixin._diff_css_classes(
        ...     {"background": True, "font-size": "normal"},
        ...     {"background": True, "font-size": "large"}
        ... )
        {'font-size': 'large'}

        Keys that were True in existing but missing in css_classes are reset:
        >>> CssParentMixin._diff_css_classes({"invisible": True}, {})
        {'invisible': False}
        """
        changed = {}
        for key, value in css_classes.items():
            if value != existing_css_classes.get(key):
                changed[key] = value

        # Detect removed boolean classes: True in existing, missing in new → reset
        for key, existing_value in existing_css_classes.items():
            if existing_value is True and key not in css_classes:
                changed[key] = False
        return changed

    @staticmethod
    def _format_css_class(key, value, breakpoint=None):
        prefix = "xprez"
        if breakpoint is not None:
            prefix += f"-{breakpoint}"

        if value is True:
            return f"{prefix}-{key}"
        elif value is False:
            return f"{prefix}-{key}-reset"
        else:
            return f"{prefix}-{key}-{value}"

    def render_css_classes(self):
        result = []

        # Parent classes (no breakpoint prefix)
        for key, value in self.get_css_classes().items():
            result += [self._format_css_class(key, value)]

        # Config classes (with breakpoint prefix)
        for breakpoint, css_classes in self.get_css_classes_by_breakpoint().items():
            for key, value in css_classes.items():
                result += [self._format_css_class(key, value, breakpoint)]

        return " ".join(result)
