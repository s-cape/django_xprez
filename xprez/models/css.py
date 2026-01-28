from xprez import constants
from xprez.conf import settings

"TODO: this file need cleanup"


def _get_unit_string(mapping, choice=None):
    """Extract unit string from mapping, handling dict or string units."""
    if not mapping:
        return ""

    units = mapping.get("units", "")
    if isinstance(units, dict):
        if choice:
            return units.get(choice, "")
        return ""
    elif units:
        return units
    return ""


class ChoiceUnitsProxy:
    """Proxy to access choice-specific units."""

    def __init__(self, mapping):
        self.mapping = mapping

    def __getattr__(self, choice):
        """
        Returns unit for specific choice: config.units.max_width.small -> 'px'
        """
        return _get_unit_string(self.mapping, choice)


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
        mapping = self.config._get_css_mapping(field_name)
        return ChoiceUnitsProxy(mapping)


class CssMixin:
    """Base mixin for CSS generation from config fields."""

    def get_css(self):
        return {}

    def _get_choice_or_custom(self, field_prefix):
        """Get CSS value - transformed choice or formatted custom."""
        choice_value = getattr(self, f"{field_prefix}_choice")
        if choice_value == constants.CUSTOM:
            return self._format_css_value(
                self._get_css_mapping(field_prefix),
                getattr(self, f"{field_prefix}_custom"),
                choice_value,
            )
        else:
            return self._transform_css(field_prefix, choice_value)

    def _transform_css(self, attr, value):
        """("margin_bottom", "small") -> "20px" """
        mapping = self._get_css_mapping(attr)
        breakpoints = mapping.get("values", {}).get(value) if mapping else None
        if not breakpoints:
            return value
        raw = self._resolve_breakpoint(breakpoints)
        return self._format_css_value(mapping, raw, value)

    def _get_css_mapping(self, attr):
        """Get XPREZ_CSS mapping for attr, trying keys in order with fallback to default."""
        css = settings.XPREZ_CSS
        for key in self.get_css_config_keys():
            # Support dot notation for nested keys (e.g., "module.xprez.GalleryModule")
            config = css
            for part in key.split("."):
                config = config.get(part, {})
            mapping = config.get(attr)
            if mapping:
                return mapping
        # Fallback to top-level default
        return css.get("default", {}).get(attr)

    def _resolve_breakpoint(self, breakpoints):
        """Get value for current breakpoint, falling back to lower."""
        for bp in range(self.css_breakpoint, -1, -1):
            if bp in breakpoints:
                return breakpoints[bp]
        return None

    def _format_css_value(self, mapping, value, choice=None):
        """Apply units from mapping to value."""
        if value is None:
            return ""

        units = _get_unit_string(mapping, choice)
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

    Provides its own get_css() AND aggregates get_css() from child configs,
    merging them across breakpoints into a single <style> tag.
    """

    css_breakpoint = settings.XPREZ_DEFAULT_BREAKPOINT

    def get_css(self):
        return {}

    def get_css_by_breakpoint(self):
        """
        Compute changed css per breakpoint (compared to defaults).

        Returns: {0: {"columns": 2}, 2: {"columns": 3}}
        """
        db_configs = {
            c.css_breakpoint: c for c in self.get_configs().filter(visible=True)
        }
        current_css = self.build_config(settings.XPREZ_DEFAULT_BREAKPOINT).get_css()
        result = {}
        last_config = None

        parent_css = self.get_css()
        if parent_css:
            result[0] = parent_css

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

            css = {
                **result.get(breakpoint, {}),  # parent_css - if present
                **self._diff_css(current_css, config.get_css()),
            }
            result[breakpoint] = css
            current_css.update(css)

        return result

    @staticmethod
    def _diff_css(base_css, css):
        """
        Return only css that differs from base.

        ({"a": 1, "b": 2}, {"a": 1, "b": 3, "c": 4}) -> {"b": 3, "c": 4}
        """
        changed = {}
        for key, value in css.items():
            if value != base_css.get(key):
                changed[key] = value
        return changed

    @staticmethod
    def _format_css_vars(css):
        """
        Convert dict to CSS variables string.

        {"columns": 2, "gap": "1rem"} -> "--x-columns: 2; --x-gap: 1rem"
        """
        result = []
        for k, v in css.items():
            if isinstance(v, dict):
                continue
            result.append(f"--x-{k}: {v}")
        return "; ".join(result)

    @staticmethod
    def _format_css_rule(selector, breakpoint, css):
        """
        Wrap CSS vars in selector and media query (if breakpoint has min_width).

        ("#id", 0, {"a": 1}) -> "#id { --x-a: 1; }"
        ("#id", 2, {"a": 1}) -> "@media (min-width: 768px) { #id { --x-a: 1; } }"
        """
        if not css:
            return ""

        css_vars = CssParentMixin._format_css_vars(css)
        min_width = settings.XPREZ_BREAKPOINTS[breakpoint]["min_width"]
        rule = f"{selector} {{ {css_vars}; }}"
        if not min_width:
            return rule
        else:
            return f"@media (min-width: {min_width}px) {{ {rule} }}"

    def render_css(self):
        """
        Generate <style> tag with all breakpoint styles.

        Returns: "<style>#section-config-1 { --x-columns: 1; }</style>"
        """
        css_data = self.get_css_by_breakpoint()
        if not css_data:
            return ""

        selector = "#" + self.key
        output = []

        for breakpoint, css in css_data.items():
            rule = self._format_css_rule(selector, breakpoint, css)
            if rule:
                output += [rule]

        if output:
            return "<style>" + "".join(output) + "</style>"
        else:
            return ""
