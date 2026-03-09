from django.utils.functional import cached_property

from xprez import constants
from xprez.conf import settings


class ResponsiveImageParentMixin:
    """
    Mixin for modules that own a section and provide responsive widths and sizes.
    (E.g. GalleryModule)
    """

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
        """Return (max_width, effective_columns) per breakpoint;"""
        breakpoints = settings.XPREZ_BREAKPOINTS
        return [(breakpoints[bp]["max_width"], 1) for bp in breakpoints]

    def get_column_ranges(self):
        """
        Return (max_width_px, [(max_width, effective_columns), ...])
        collapsing consecutive duplicates.
        """
        max_width = self.get_section_max_width_px()
        ranges = []
        for bp_max_width, effective_columns in self.get_breakpoint_ranges():
            if not ranges or ranges[-1][1] != effective_columns:
                ranges += [(bp_max_width, effective_columns)]
        return max_width, ranges

    @cached_property
    def get_image_sizes(self):
        """Build HTML sizes attribute string for responsive images."""
        max_width, column_ranges = self.get_column_ranges()
        return self.build_image_sizes(max_width, column_ranges)

    @staticmethod
    def parse_crop_string(crop_str):
        """
        Parse a crop string like '3/2' into (3, 2), or return None if absent/invalid.
        """
        if not crop_str or "/" not in crop_str:
            return None
        else:
            num, den = crop_str.split("/", 1)
            return (int(num.strip()), int(den.strip()))

    @staticmethod
    def build_image_sizes(max_width, column_ranges):
        """Build HTML sizes string from (max_width_px, [(max_width, cols), ...])."""
        entries = []
        for bp_max_width, effective_columns in column_ranges:
            pct = round(100 / effective_columns, 2)
            vw_size = f"{int(pct) if pct == int(pct) else pct}vw"
            if max_width is None:
                value = vw_size
            elif bp_max_width is None or bp_max_width >= max_width:
                value = f"{round(max_width / effective_columns)}px"
            else:
                value = vw_size
            entries += [
                f"(max-width: {bp_max_width}px) {value}" if bp_max_width else value
            ]
        return ", ".join(entries)


class ResponsiveImageItemMixin:
    """
    Mixin for individual image items that produce srcset geometry strings.
    (E.g. GalleryItem)
    """

    def get_image_field(self):
        """Return the ImageField instance for this item (e.g. self.file)."""
        raise NotImplementedError

    def get_image_aspect_ratio(self):
        """Return (numerator, denominator) for the image aspect ratio."""
        raise NotImplementedError

    @cached_property
    def get_srcset_geometries(self):
        """List of 'WxH' geometry strings for srcset, capped at image's natural width."""
        try:
            cap_width = self.get_image_field().width or None
        except (AttributeError, OSError):
            cap_width = None
        numerator, denominator = self.get_image_aspect_ratio()
        return self.build_srcset_geometries(
            settings.XPREZ_SRCSET_WIDTHS, numerator, denominator, cap_width
        )

    @staticmethod
    def build_srcset_geometries(
        widths, aspect_numerator, aspect_denominator, cap_width=None
    ):
        """Return list of 'WxH' geometry strings, capped at cap_width if given."""
        if cap_width is None:
            final = list(widths)
        else:
            final = [w for w in widths if w < cap_width] + [cap_width]
        return [
            f"{w}x{round(w * aspect_denominator / aspect_numerator)}" for w in final
        ]


class ResponsiveImageSourcesMixin:
    """
    Mixin for modules whose breakpoint configs each carry a crop string.
    Produces the source list for <picture>/<img> art-direction rendering.

    Requires build_srcset_geometries (from ResponsiveImageItemMixin).
    Subclasses must implement get_config_crop(config).
    """

    def get_config_crop(self, config):
        """Return the crop string (e.g. '3/2') for a config instance, or None."""
        raise NotImplementedError

    @cached_property
    def get_media_image_sources(self):
        """
        Return a list of dicts for <picture> rendering, ordered for correct browser
        matching (smallest max_width first; base/fallback last with max_width=None).

        Each dict: max_width (int or None), thumbnail_crop (str), geometries (list).
        Non-base entries with a crop differing from the base become <source> elements;
        the final entry (max_width=None) is always the <img> fallback.
        """
        breakpoints = settings.XPREZ_BREAKPOINTS
        saved = {c.css_breakpoint: c for c in self.get_saved_configs()}

        base_config = saved.get(0)
        base_crop_str = self.get_config_crop(base_config) if base_config else None
        base_crop = self.parse_crop_string(base_crop_str)

        non_base_bp_ids = sorted(
            [bp_id for bp_id in saved if bp_id != 0],
            key=lambda bp_id: breakpoints[bp_id]["max_width"],
        )

        sources = []
        for bp_id in non_base_bp_ids:
            config = saved[bp_id]
            crop = self.parse_crop_string(self.get_config_crop(config))
            if crop == base_crop:
                continue
            num, den = crop if crop else (1, 1)
            sources += [
                {
                    "max_width": breakpoints[bp_id]["max_width"],
                    "thumbnail_crop": "center" if crop else "",
                    "geometries": self.build_srcset_geometries(
                        settings.XPREZ_SRCSET_WIDTHS, num, den
                    ),
                }
            ]

        num, den = base_crop if base_crop else (1, 1)
        sources += [
            {
                "max_width": None,
                "thumbnail_crop": "center" if base_crop else "",
                "geometries": self.build_srcset_geometries(
                    settings.XPREZ_SRCSET_WIDTHS, num, den
                ),
            }
        ]
        return sources


class ResponsiveImageMixin(ResponsiveImageParentMixin, ResponsiveImageItemMixin):
    """
    Combined mixin for when parent and item are the same object.
    (E.g. TextModule, VideoModule)
    """
