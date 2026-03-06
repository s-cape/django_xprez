from django.utils.functional import cached_property

from xprez import constants
from xprez.conf import settings


def _format_percentage(value):
    rounded = round(value, 2)
    return int(rounded) if rounded == int(rounded) else rounded


def _media_entry(value, breakpoint=None):
    """Wrap value in a CSS media query if breakpoint is given."""
    if breakpoint:
        return f"(max-width: {breakpoint}px) {value}"
    return value


def _build_image_sizes(max_width, column_ranges):
    """Build HTML sizes string from (max_width_px, [(max_width, cols), ...])."""
    entries = []
    for index, (bp_max_width, effective_columns) in enumerate(column_ranges):
        if index > 0:
            prev_max_width = column_ranges[index - 1][0]
        else:
            prev_max_width = None
        vw_size = f"{_format_percentage(100 / effective_columns)}vw"
        if max_width is None:
            entries += [_media_entry(vw_size, bp_max_width)]
        elif bp_max_width is None or bp_max_width >= max_width:
            px_size = round(max_width / effective_columns)
            entries += [_media_entry(f"{px_size}px", bp_max_width)]
        elif prev_max_width is None or prev_max_width < max_width:
            entries += [_media_entry(vw_size, bp_max_width)]
        else:
            entries += [_media_entry(vw_size, bp_max_width)]
    return ", ".join(entries)


def _round_boundary_up(px):
    """Round a breakpoint boundary up to the nearest 100 for clean srcset steps."""
    return ((px + 99) // 100) * 100


def _build_srcset_widths(max_width, full_width_cap, breakpoint_ranges):
    """Compute candidate srcset widths (1x + 2x) from breakpoint ranges, capped."""
    if max_width is None:
        max_boundary = full_width_cap
    else:
        max_boundary = min(max_width, full_width_cap)
    retina_cap = full_width_cap * 2
    candidate_widths = set()
    for bp_max_width, effective_columns, _prev_max_width in breakpoint_ranges:
        if bp_max_width is None or bp_max_width >= max_boundary:
            boundary = max_boundary
        else:
            boundary = _round_boundary_up(bp_max_width)
        pixel_width = round(boundary / effective_columns)
        candidate_widths.add(pixel_width)
        candidate_widths.add(pixel_width * 2)
    return sorted(width for width in candidate_widths if 0 < width <= retina_cap)


def build_srcset_geometries(
    widths, aspect_numerator, aspect_denominator, cap_width=None
):
    """Return list of 'WxH' geometry strings, optionally capped at cap_width."""
    capped = [w for w in widths if cap_width is None or w <= cap_width]
    if not capped:
        capped = [cap_width] if cap_width else list(widths)[:1]
    return [f"{w}x{round(w * aspect_denominator / aspect_numerator)}" for w in capped]


class ResponsiveImageParentMixin:
    """Mixin for modules that own a section and provide responsive widths and sizes."""

    def get_section_max_width_px(self):
        """Section max-width in px, or None for full-width."""
        width_choice = self.section.max_width_choice
        if width_choice == constants.MAX_WIDTH_FULL:
            return None
        elif width_choice == constants.MAX_WIDTH_CUSTOM:
            return self.section.max_width_custom or None
        else:
            max_width_values = settings.XPREZ_CSS["section"]["max_width"]["values"]
            return max_width_values.get(width_choice, {}).get(0)

    def get_breakpoint_ranges(self):
        """
        Return (max_width, effective_columns, prev_max_width) per breakpoint;
        default is single-column.
        """
        breakpoints = settings.XPREZ_BREAKPOINTS
        widths = [breakpoints[bp]["max_width"] for bp in breakpoints]
        return [(w, 1, widths[i - 1] if i > 0 else None) for i, w in enumerate(widths)]

    def get_column_ranges(self):
        """
        Return (max_width_px, [(max_width, effective_columns), ...])
        collapsing consecutive duplicates.
        """
        max_width = self.get_section_max_width_px()
        ranges = []
        for bp_max_width, effective_columns, _ in self.get_breakpoint_ranges():
            if not ranges or ranges[-1][1] != effective_columns:
                ranges += [(bp_max_width, effective_columns)]
        return max_width, ranges

    @cached_property
    def get_srcset_widths(self):
        """Candidate widths for srcset, capped at XPREZ_GALLERY_FULL_WIDTH_PX."""
        max_width = self.get_section_max_width_px()
        full_width_cap = settings.XPREZ_GALLERY_FULL_WIDTH_PX
        return _build_srcset_widths(
            max_width, full_width_cap, self.get_breakpoint_ranges()
        )

    @cached_property
    def get_image_sizes(self):
        """Build HTML sizes attribute string for responsive images."""
        max_width, column_ranges = self.get_column_ranges()
        return _build_image_sizes(max_width, column_ranges)


class ResponsiveImageItemMixin:
    """Mixin for individual image items that produce srcset geometry strings."""

    def get_image_field(self):
        """
        Return the ImageField instance for this item
        (e.g. self.file, self.poster_image).
        """
        raise NotImplementedError

    def get_aspect_ratio(self):
        """Return (numerator, denominator) for the image aspect ratio."""
        raise NotImplementedError

    def get_srcset_widths_for_geometries(self):
        """Return list of candidate widths for geometry generation."""
        raise NotImplementedError

    @cached_property
    def get_srcset_geometries(self):
        """
        List of 'WxH' geometry strings for srcset,
        capped at image's natural width.
        """
        try:
            cap_width = self.get_image_field().width
        except Exception:
            cap_width = None
        if not cap_width:
            cap_width = settings.XPREZ_GALLERY_FULL_WIDTH_PX
        numerator, denominator = self.get_aspect_ratio()
        return build_srcset_geometries(
            self.get_srcset_widths_for_geometries(), numerator, denominator, cap_width
        )


class ResponsiveImageMixin(ResponsiveImageParentMixin, ResponsiveImageItemMixin):
    """
    Combined mixin for when parent and item are the same object
    (e.g. VideoModule's poster)
    """

    def get_srcset_widths_for_geometries(self):
        return self.get_srcset_widths
