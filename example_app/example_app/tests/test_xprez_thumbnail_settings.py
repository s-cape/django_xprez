"""Tests for XPREZ_THUMBNAIL settings and get_thumbnail_options."""

from django.test import TestCase, override_settings

from xprez.conf import settings as xprez_settings
from xprez.conf import defaults
from xprez.utils import get_thumbnail_options


def _clear_xprez_thumbnail_cache():
    if hasattr(xprez_settings, "XPREZ_THUMBNAIL"):
        delattr(xprez_settings, "XPREZ_THUMBNAIL")


class GetThumbnailOptionsTest(TestCase):
    def setUp(self):
        _clear_xprez_thumbnail_cache()

    def test_responsive_image_inherits_default(self):
        opts = get_thumbnail_options("responsive_image")
        self.assertEqual(opts["quality"], 70)
        self.assertEqual(opts["format"], "WEBP")

    def test_quote_quality(self):
        opts = get_thumbnail_options("quote")
        self.assertEqual(opts["quality"], 80)
        self.assertEqual(opts["format"], "WEBP")

    def test_gallery_lightbox_quality(self):
        opts = get_thumbnail_options("gallery_lightbox")
        self.assertEqual(opts["quality"], 90)

    def test_admin_gallery_item(self):
        opts = get_thumbnail_options("admin_gallery_item")
        self.assertEqual(opts["quality"], 80)

    def test_admin_file_preview(self):
        opts = get_thumbnail_options("admin_file_preview")
        self.assertEqual(opts["quality"], 80)

    def test_admin_template_container_inherits_default(self):
        opts = get_thumbnail_options("admin_template_container")
        self.assertEqual(opts["quality"], 70)
        self.assertEqual(opts["format"], "WEBP")

    def test_unknown_use_falls_back_to_default(self):
        opts = get_thumbnail_options("unknown_use")
        self.assertEqual(opts["quality"], 70)
        self.assertEqual(opts["format"], "WEBP")

    @override_settings(
        XPREZ_THUMBNAIL={
            "quote": {"quality": None},
        }
    )
    def test_none_quality_inherits_default(self):
        _clear_xprez_thumbnail_cache()
        merged = xprez_settings.XPREZ_THUMBNAIL
        self.assertEqual(merged["quote"]["quality"], None)
        opts = get_thumbnail_options("quote")
        self.assertEqual(opts["quality"], 70)


class XPREZThumbnailMergeTest(TestCase):
    def setUp(self):
        _clear_xprez_thumbnail_cache()

    @override_settings(
        XPREZ_THUMBNAIL={
            "quote": {"quality": 85},
        }
    )
    def test_partial_override_merges_other_keys(self):
        _clear_xprez_thumbnail_cache()
        merged = xprez_settings.XPREZ_THUMBNAIL
        self.assertEqual(merged["quote"]["quality"], 85)
        self.assertIn("responsive_image", merged)
        self.assertIn("gallery_lightbox", merged)
        self.assertEqual(merged["gallery_lightbox"]["quality"], 90)

    @override_settings(
        XPREZ_THUMBNAIL={
            "default": {"quality": 75},
        }
    )
    def test_default_quality_override_propagates(self):
        _clear_xprez_thumbnail_cache()
        self.assertEqual(xprez_settings.XPREZ_THUMBNAIL["default"]["quality"], 75)
        opts = get_thumbnail_options("responsive_image")
        self.assertEqual(opts["quality"], 75)

    def test_library_defaults_has_all_use_keys(self):
        expected = {
            "default",
            "responsive_image",
            "quote",
            "gallery_lightbox",
            "admin_gallery_item",
            "admin_file_preview",
            "admin_template_container",
        }
        self.assertEqual(set(defaults.XPREZ_THUMBNAIL.keys()), expected)
