"""Tests for video URL parsing and VideoForm (video_type, video_id)."""

from django.test import TestCase

from example_app.models import Page
from xprez.models import Section
from xprez.modules.video import VimeoVideoProvider, VideoForm, YouTubeVideoProvider


class VideoProviderExampleUrlsTest(TestCase):
    """Example URLs from each provider must match and return correct video_id."""

    def test_youtube_example_watch_returns_expected_id(self):
        url = "https://www.youtube.com/watch?v=nNGBxXN7QC0"
        self.assertEqual(YouTubeVideoProvider().get_id(url), "nNGBxXN7QC0")

    def test_youtube_short_url_returns_expected_id(self):
        url = "https://youtu.be/nNGBxXN7QC0"
        self.assertEqual(YouTubeVideoProvider().get_id(url), "nNGBxXN7QC0")

    def test_youtube_embed_url_returns_expected_id(self):
        url = "https://www.youtube.com/embed/nNGBxXN7QC0"
        self.assertEqual(YouTubeVideoProvider().get_id(url), "nNGBxXN7QC0")

    def test_vimeo_example_returns_expected_id(self):
        url = "https://vimeo.com/210073083"
        self.assertEqual(VimeoVideoProvider().get_id(url), "210073083")

    def test_vimeo_video_path_returns_expected_id(self):
        url = "https://vimeo.com/video/210073083"
        self.assertEqual(VimeoVideoProvider().get_id(url), "210073083")

    def test_youtube_substring_in_foreign_host_returns_none(self):
        url = "https://example.com/?next=youtube.com/watch?v=nNGBxXN7QC0"
        self.assertIsNone(YouTubeVideoProvider().get_id(url))


class VideoFormExampleUrlsTest(TestCase):
    """VideoForm must set video_type and video_id correctly for example URLs."""

    def _form_data(self, url, section, position=0):
        return {
            "url": url,
            "section": section.pk,
            "position": position,
            "delete": False,
        }

    def test_youtube_example_sets_video_type_and_id(self):
        page = Page.objects.create(title="P", slug="p")
        section = Section.objects.create(container=page, position=0, saved=True)
        url = "https://www.youtube.com/watch?v=nNGBxXN7QC0"
        form = VideoForm(data=self._form_data(url, section))
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.video_type, "youtube")
        self.assertEqual(form.video_id, "nNGBxXN7QC0")

    def test_vimeo_example_sets_video_type_and_id(self):
        page = Page.objects.create(title="P", slug="p")
        section = Section.objects.create(container=page, position=0, saved=True)
        url = "https://vimeo.com/210073083"
        form = VideoForm(data=self._form_data(url, section))
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.video_type, "vimeo")
        self.assertEqual(form.video_id, "210073083")

    def test_unsupported_url_raises_validation_error(self):
        page = Page.objects.create(title="P", slug="p")
        section = Section.objects.create(container=page, position=0, saved=True)
        form = VideoForm(
            data=self._form_data("https://example.com/not-a-video", section)
        )
        self.assertFalse(form.is_valid())
        self.assertIn("url", form.errors)

    def test_youtube_substring_in_foreign_host_raises_validation_error(self):
        page = Page.objects.create(title="P", slug="p")
        section = Section.objects.create(container=page, position=0, saved=True)
        form = VideoForm(
            data=self._form_data(
                "https://example.com/?next=youtube.com/watch?v=nNGBxXN7QC0", section
            )
        )
        self.assertFalse(form.is_valid())
        self.assertIn("url", form.errors)
