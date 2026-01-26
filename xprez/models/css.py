from xprez.conf import settings

"TODO: this file need cleanup"


class UnitsProxy:
    """Proxy to access units from XPREZ_CSS for any field."""

    def __init__(self, config):
        self.config = config

    def __getattr__(self, field_name):
        """Returns units for any field: config.units.margin_bottom -> 'px'"""
        mapping = self.config._get_css_mapping(field_name)
        return mapping.get("units", "") if mapping else ""


class CssConfigMixin:
    """Mixin for ConfigBase to transform placeholder CSS values."""

    def _transform_css(self, attr, value):
        """("margin_bottom", "small") -> "20px" """
        mapping = self._get_css_mapping(attr)
        breakpoints = mapping.get("values", {}).get(value) if mapping else None
        if not breakpoints:
            return value
        raw = self._resolve_breakpoint(breakpoints)
        return self._format_css_value(mapping, raw)

    def _get_css_mapping(self, attr):
        """Get XPREZ_CSS mapping for attr, trying keys in order."""
        css = settings.XPREZ_CSS
        for key in self._get_css_config_keys():
            mapping = css.get(key, {}).get(attr)
            if mapping:
                return mapping
        return None

    def _resolve_breakpoint(self, breakpoints):
        """Get value for current breakpoint, falling back to lower."""
        for bp in range(self.css_breakpoint, -1, -1):
            if bp in breakpoints:
                return breakpoints[bp]
        return None

    def _format_css_value(self, mapping, value):
        """Apply units from mapping to value."""
        units = mapping.get("units", "") if mapping else ""
        return f"{value}{units}" if value is not None else value

    @property
    def units(self):
        """Proxy for accessing units: config.units.margin_bottom"""
        return UnitsProxy(self)

    def _get_css_config_keys(self):
        """Return keys for XPREZ_CSS lookup in priority order. Override in subclasses."""
        raise NotImplementedError()


class CssRenderMixin:
    """Mixin for rendering responsive CSS from config breakpoints."""

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

            css = config.get_css()
            changed = self._diff_css(current_css, css)
            if changed:
                result[breakpoint] = changed
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
        return "; ".join(f"--x-{k}: {v}" for k, v in css.items())

    @staticmethod
    def _format_css_rule(selector, breakpoint, css):
        """
        Wrap CSS vars in selector and media query (if breakpoint has min_width).

        ("#id", 0, {"a": 1}) -> "#id { --x-a: 1; }"
        ("#id", 2, {"a": 1}) -> "@media (min-width: 768px) { #id { --x-a: 1; } }"
        """
        css_vars = CssRenderMixin._format_css_vars(css)
        min_width = settings.XPREZ_BREAKPOINTS[breakpoint]["min_width"]
        rule = f"{selector} {{ {css_vars}; }}"
        if not min_width:
            return rule
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
            output += [self._format_css_rule(selector, breakpoint, css)]

        if output:
            return "<style>" + "".join(output) + "</style>"
        else:
            return ""
