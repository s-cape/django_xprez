"""Tests for responsive image sizes/srcset (ResponsiveImageMixin, gallery, video)."""

from django.test import TestCase

from example_app.models import Page
from xprez import constants
from xprez.conf import settings
from xprez.models import (
    GalleryConfig,
    GalleryModule,
    Section,
    SectionConfig,
    VideoModule,
)
from xprez.models.mixins.responsive_image import (
    _build_image_sizes,
    _build_srcset_widths,
    build_srcset_geometries,
)


def _create_page_and_section(max_width_choice=None, max_width_custom=None):
    page = Page.objects.create(title="P", slug="p")
    section_kwargs = {"container": page, "saved": True}
    if max_width_choice is not None:
        section_kwargs["max_width_choice"] = max_width_choice
    if max_width_custom is not None:
        section_kwargs["max_width_custom"] = max_width_custom
    section = Section.objects.create(**section_kwargs)
    return section


class ResponsiveImageHelpersTest(TestCase):
    """Unit tests for pure helper functions in responsive_image module."""

    def test_build_srcset_geometries_16_9_returns_wxh(self):
        widths = [500, 1000]
        result = build_srcset_geometries(widths, 16, 9, cap_width=None)
        self.assertEqual(result, ["500x281", "1000x562"])

    def test_build_srcset_geometries_caps_at_cap_width(self):
        widths = [500, 1000, 1500]
        result = build_srcset_geometries(widths, 16, 9, cap_width=800)
        self.assertEqual(result, ["500x281"])

    def test_build_srcset_geometries_square_ratio(self):
        widths = [200, 400]
        result = build_srcset_geometries(widths, 1, 1, cap_width=None)
        self.assertEqual(result, ["200x200", "400x400"])

    def test_build_srcset_geometries_uses_cap_when_all_widths_exceed_it(self):
        widths = [1000, 1200]
        result = build_srcset_geometries(widths, 16, 9, cap_width=800)
        self.assertEqual(result, ["800x450"])

    def test_build_image_sizes_single_column_full_width(self):
        max_width = None
        column_ranges = [(0, 1), (500, 1), (768, 1)]
        result = _build_image_sizes(max_width, column_ranges)
        self.assertEqual(
            result,
            "(max-width: 500px) 100vw, (max-width: 768px) 100vw, 100vw",
        )

    def test_build_image_sizes_single_column_capped(self):
        max_width = 1296
        column_ranges = [(0, 1)]
        result = _build_image_sizes(max_width, column_ranges)
        self.assertEqual(result, "(max-width: 1296px) 100vw, 1296px")

    def test_build_image_sizes_two_columns(self):
        max_width = 1296
        column_ranges = [(0, 1), (768, 2)]
        result = _build_image_sizes(max_width, column_ranges)
        self.assertEqual(
            result,
            "(max-width: 768px) 100vw, (max-width: 1296px) 50vw, 648px",
        )

    def test_build_srcset_widths_single_column_capped(self):
        max_width = 1296
        full_width_cap = settings.XPREZ_GALLERY_FULL_WIDTH_PX
        breakpoint_ranges = [(0, 1, 500), (500, 1, 768), (768, 1, None)]
        result = _build_srcset_widths(max_width, full_width_cap, breakpoint_ranges)
        self.assertIsInstance(result, list)
        self.assertEqual(result, sorted(result))
        self.assertTrue(all(0 < w <= full_width_cap * 2 for w in result))

    def test_build_srcset_widths_exact_boundaries_with_max_width(self):
        result = _build_srcset_widths(
            max_width=900,
            full_width_cap=1000,
            breakpoint_ranges=[(0, 1, 500), (500, 2, 1200), (1200, 3, None)],
        )
        self.assertEqual(result, [300, 450, 500, 600, 900, 1000])

    def test_build_srcset_widths_exact_boundaries_full_width(self):
        result = _build_srcset_widths(
            max_width=None,
            full_width_cap=1000,
            breakpoint_ranges=[(0, 1, 500), (500, 2, None)],
        )
        self.assertEqual(result, [500, 1000])


class VideoModuleSizesTest(TestCase):
    """VideoModule get_section_max_width_px, get_srcset_widths, get_image_sizes."""

    def _video_module(self, section):
        return VideoModule.objects.create(
            section=section,
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            video_type="youtube",
            video_id="dQw4w9WgXcQ",
            position=0,
            saved=True,
        )

    def test_section_full_width_get_section_max_width_px_none(self):
        section = _create_page_and_section(max_width_choice=constants.MAX_WIDTH_FULL)
        module = self._video_module(section)
        self.assertIsNone(module.get_section_max_width_px())

    def test_section_medium_width_get_section_max_width_px_1296(self):
        section = _create_page_and_section(max_width_choice=constants.MAX_WIDTH_MEDIUM)
        module = self._video_module(section)
        self.assertEqual(module.get_section_max_width_px(), 1296)

    def test_section_small_width_get_section_max_width_px_720(self):
        section = _create_page_and_section(max_width_choice=constants.MAX_WIDTH_SMALL)
        module = self._video_module(section)
        self.assertEqual(module.get_section_max_width_px(), 720)

    def test_get_breakpoint_ranges_yields_single_column(self):
        section = _create_page_and_section()
        module = self._video_module(section)
        ranges = list(module.get_breakpoint_ranges())
        self.assertGreater(len(ranges), 0)
        for min_width, effective_columns, next_min_width in ranges:
            self.assertEqual(effective_columns, 1)
            self.assertIsInstance(min_width, int)
            self.assertTrue(next_min_width is None or isinstance(next_min_width, int))

    def test_get_srcset_widths_non_empty_sorted_capped(self):
        section = _create_page_and_section()
        module = self._video_module(section)
        widths = module.get_srcset_widths
        self.assertGreater(len(widths), 0)
        self.assertEqual(widths, sorted(widths))
        cap = settings.XPREZ_GALLERY_FULL_WIDTH_PX * 2
        self.assertTrue(all(0 < w <= cap for w in widths))

    def test_get_image_sizes_full_width_contains_100vw(self):
        section = _create_page_and_section(max_width_choice=constants.MAX_WIDTH_FULL)
        module = self._video_module(section)
        self.assertEqual(module.get_image_sizes, "100vw")

    def test_get_image_sizes_medium_width_contains_1296px(self):
        section = _create_page_and_section(max_width_choice=constants.MAX_WIDTH_MEDIUM)
        module = self._video_module(section)
        self.assertEqual(
            module.get_image_sizes,
            "(max-width: 1296px) 100vw, 1296px",
        )

    def test_section_custom_width_get_section_max_width_px_custom(self):
        section = _create_page_and_section(
            max_width_choice=constants.MAX_WIDTH_CUSTOM,
            max_width_custom=888,
        )
        module = self._video_module(section)
        self.assertEqual(module.get_section_max_width_px(), 888)


class GalleryModuleSizesTest(TestCase):
    """GalleryModule get_srcset_widths/get_image_sizes for section+config variants."""

    def _gallery_module(self, section):
        return GalleryModule.objects.create(section=section, position=0, saved=True)

    def test_section_default_one_column_sizes_contains_vw_or_px(self):
        section = _create_page_and_section()
        module = self._gallery_module(section)
        sizes = module.get_image_sizes
        self.assertIsInstance(sizes, str)
        self.assertTrue("vw" in sizes or "px" in sizes)
        self.assertIn("(max-width:", sizes)

    def test_section_medium_get_srcset_widths_non_empty(self):
        section = _create_page_and_section(max_width_choice=constants.MAX_WIDTH_MEDIUM)
        module = self._gallery_module(section)
        widths = module.get_srcset_widths
        self.assertGreater(len(widths), 0)
        self.assertEqual(widths, sorted(widths))

    def test_section_full_width_gallery_single_column_sizes_contains_100vw(self):
        section = _create_page_and_section(max_width_choice=constants.MAX_WIDTH_FULL)
        module = self._gallery_module(section)
        config = module.get_configs().get(
            css_breakpoint=settings.XPREZ_DEFAULT_BREAKPOINT
        )
        config.columns = 1
        config.saved = True
        config.save()
        self.assertEqual(module.get_image_sizes, "100vw")

    def test_gallery_sizes_reflect_section_two_columns_at_breakpoint(
        self,
    ):
        section = _create_page_and_section()
        SectionConfig.objects.create(
            section=section,
            css_breakpoint=1,
            columns=2,
            saved=True,
        )
        module = self._gallery_module(section)
        config = module.get_configs().get(
            css_breakpoint=settings.XPREZ_DEFAULT_BREAKPOINT
        )
        config.columns = 1
        config.saved = True
        config.save()
        self.assertEqual(
            module.get_image_sizes,
            "(max-width: 500px) 100vw, (max-width: 1296px) 50vw, 648px",
        )

    def test_section_medium_gallery_two_columns_sizes_has_half_max_width_px(self):
        section = _create_page_and_section(max_width_choice=constants.MAX_WIDTH_MEDIUM)
        gallery = GalleryModule.objects.create(section=section, position=0, saved=True)
        config = gallery.get_configs().get(
            css_breakpoint=settings.XPREZ_DEFAULT_BREAKPOINT
        )
        config.columns = 2
        config.saved = True
        config.save()
        self.assertEqual(
            gallery.get_image_sizes,
            "(max-width: 1296px) 50vw, 648px",
        )

    def test_section_and_gallery_multi_breakpoint_configs_exact_sizes(self):
        """Section and gallery have different columns/colspan; assert exact sizes."""
        section = _create_page_and_section(max_width_choice=constants.MAX_WIDTH_MEDIUM)
        section_c0 = section.get_configs().get(css_breakpoint=0)
        section_c0.columns = 1
        section_c0.saved = True
        section_c0.save()
        SectionConfig.objects.create(
            section=section, css_breakpoint=1, columns=2, saved=True
        )
        SectionConfig.objects.create(
            section=section, css_breakpoint=2, columns=4, saved=True
        )
        gallery = GalleryModule.objects.create(section=section, position=0, saved=True)
        gallery_c0 = gallery.get_configs().get(css_breakpoint=0)
        gallery_c0.columns = 1
        gallery_c0.saved = True
        gallery_c0.save()
        GalleryConfig.objects.create(
            module=gallery, css_breakpoint=1, columns=2, saved=True
        )
        GalleryConfig.objects.create(
            module=gallery, css_breakpoint=2, columns=4, saved=True
        )
        # Effective: bp0 1*1=1, bp1 2*2=4, bp2 4*4=16 → (0,1), (500,4), (768,16)
        self.assertEqual(
            gallery.get_image_sizes,
            "(max-width: 500px) 100vw, (max-width: 768px) 25vw, "
            "(max-width: 1296px) 6.25vw, 81px",
        )

    def test_section_and_gallery_with_colspan_exact_sizes(self):
        """Gallery colspan changes effective_columns at a breakpoint."""
        section = _create_page_and_section(max_width_choice=constants.MAX_WIDTH_MEDIUM)
        sc0 = section.get_configs().get(css_breakpoint=0)
        sc0.columns = 1
        sc0.saved = True
        sc0.save()
        SectionConfig.objects.create(
            section=section, css_breakpoint=1, columns=2, saved=True
        )
        SectionConfig.objects.create(
            section=section, css_breakpoint=2, columns=4, saved=True
        )
        gallery = GalleryModule.objects.create(section=section, position=0, saved=True)
        gc0 = gallery.get_configs().get(css_breakpoint=0)
        gc0.columns = 1
        gc0.saved = True
        gc0.save()
        GalleryConfig.objects.create(
            module=gallery, css_breakpoint=1, columns=2, saved=True
        )
        GalleryConfig.objects.create(
            module=gallery,
            css_breakpoint=2,
            columns=2,
            colspan=2,
            saved=True,
        )
        # Effective: bp0 1, bp1 2*2=4, bp2 4*2//2=4 → (0,1), (500,4)
        self.assertEqual(
            gallery.get_image_sizes,
            "(max-width: 500px) 100vw, (max-width: 1296px) 25vw, 324px",
        )
