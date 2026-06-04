"""Tests for XPREZ_THUMBNAIL settings and get_thumbnail_options."""

from django.test import TestCase, override_settings

from xprez.conf import settings as xprez_settings
from xprez.utils import get_thumbnail_options


def _clear_xprez_thumbnail_cache():
    if hasattr(xprez_settings, "XPREZ_THUMBNAIL"):
        delattr(xprez_settings, "XPREZ_THUMBNAIL")


class GetThumbnailOptionsTest(TestCase):
    def setUp(self):
        _clear_xprez_thumbnail_cache()

    def test_empty_use_inherits_default(self):
        opts = get_thumbnail_options("quote")
        self.assertEqual(opts, {"quality": 70, "format": "WEBP"})

    def test_explicit_use_override(self):
        opts = get_thumbnail_options("gallery_lightbox")
        self.assertEqual(opts["quality"], 90)
        self.assertEqual(opts["format"], "WEBP")

    def test_unknown_use_falls_back_to_default(self):
        self.assertEqual(
            get_thumbnail_options("unknown_use"),
            {"quality": 70, "format": "WEBP"},
        )

    @override_settings(XPREZ_THUMBNAIL={"quote": {"quality": None}})
    def test_none_skips_override(self):
        _clear_xprez_thumbnail_cache()
        self.assertEqual(get_thumbnail_options("quote")["quality"], 70)


class XPREZThumbnailMergeTest(TestCase):
    def setUp(self):
        _clear_xprez_thumbnail_cache()

    @override_settings(XPREZ_THUMBNAIL={"quote": {"quality": 85}})
    def test_partial_host_override_deep_merges(self):
        _clear_xprez_thumbnail_cache()
        merged = xprez_settings.XPREZ_THUMBNAIL
        self.assertEqual(merged["quote"]["quality"], 85)
        self.assertEqual(merged["gallery_lightbox"]["quality"], 90)
        self.assertEqual(get_thumbnail_options("quote")["quality"], 85)

    @override_settings(XPREZ_THUMBNAIL={"default": {"quality": 75}})
    def test_default_override_propagates_to_empty_use(self):
        _clear_xprez_thumbnail_cache()
        self.assertEqual(get_thumbnail_options("responsive_image")["quality"], 75)
