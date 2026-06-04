"""Lazy sorl-thumbnail backend: payload encoding and view behavior."""

from unittest.mock import Mock, patch

from django.core.files.storage import FileSystemStorage
from django.test import TestCase
from django.urls import reverse
from sorl.thumbnail import default
from sorl.thumbnail.base import ThumbnailBackend

from sorl.thumbnail.images import ImageFile

from xprez.contrib.sorl_thumbnail.lazy.backend import (
    LazyImageFile,
    LazyThumbnailBackend,
    LazyThumbnailBackendMixin,
    decode_thumbnail_payload,
    encode_source_ref,
    encode_thumbnail_payload,
    rebuild_source,
)


class PayloadRoundtripTests(TestCase):
    def test_roundtrip_args_and_kwargs(self):
        args_in = ["images/photo.jpg", "800x600"]
        kwargs_in = {"crop": "center", "format": "WEBP", "quality": 70}
        payload, sig = encode_thumbnail_payload(*args_in, **kwargs_in)
        args_out, kwargs_out = decode_thumbnail_payload(payload, sig)
        self.assertEqual(args_out, args_in)
        self.assertEqual(kwargs_out, kwargs_in)

    def test_tampered_payload_raises(self):
        payload, sig = encode_thumbnail_payload("images/photo.jpg", "800x600")
        tampered = payload[:-1] + ("A" if payload[-1] != "A" else "B")
        with self.assertRaises(ValueError):
            decode_thumbnail_payload(tampered, sig)

    def test_tampered_sig_raises(self):
        payload, sig = encode_thumbnail_payload("images/photo.jpg", "800x600")
        bad_sig = sig[:-1] + ("0" if sig[-1] != "0" else "1")
        with self.assertRaises(ValueError):
            decode_thumbnail_payload(payload, bad_sig)


class _CustomStorage(FileSystemStorage):
    """Module-level storage so its class path round-trips through the payload."""


class SourceRefRoundtripTests(TestCase):
    def test_rebuild_preserves_key_with_custom_storage(self):
        source = ImageFile("images/photo.jpg", _CustomStorage())
        rebuilt = rebuild_source(encode_source_ref(source))
        self.assertIsInstance(rebuilt, ImageFile)
        self.assertEqual(rebuilt.key, source.key)

    def test_bare_string_loses_storage_key(self):
        """Why the fix exists: a name-only ref keys to the default storage."""
        source = ImageFile("images/photo.jpg", _CustomStorage())
        self.assertNotEqual(ImageFile("images/photo.jpg").key, source.key)

    def test_plain_string_ref_passthrough(self):
        self.assertEqual(rebuild_source("images/photo.jpg"), "images/photo.jpg")


class LazyThumbnailBackendGetThumbnailTests(TestCase):
    def test_kv_miss_returns_lazy_even_if_file_on_storage(self):
        """Only kvstore marks a thumbnail ready; disk alone does not skip lazy URL."""
        with patch.object(default.kvstore, "get", return_value=None):
            with patch.object(default.storage, "exists", return_value=True):
                with patch.object(ThumbnailBackend, "get_thumbnail") as super_gt:
                    with patch.object(
                        LazyThumbnailBackend,
                        "_get_source_dimensions",
                        return_value=[800, 600],
                    ):
                        backend = LazyThumbnailBackend()
                        result = backend.get_thumbnail(
                            "dummy.jpg", "100x100", format="JPEG"
                        )
        self.assertIsInstance(result, LazyImageFile)
        super_gt.assert_not_called()

    def test_missing_file_returns_lazy_placeholder(self):
        with patch.object(default.kvstore, "get", return_value=None):
            with patch.object(default.storage, "exists", return_value=False):
                with patch.object(ThumbnailBackend, "get_thumbnail") as super_gt:
                    with patch.object(
                        LazyThumbnailBackend,
                        "_get_source_dimensions",
                        return_value=[800, 600],
                    ):
                        backend = LazyThumbnailBackend()
                        result = backend.get_thumbnail(
                            "dummy.jpg", "100x100", format="JPEG"
                        )
        self.assertIsInstance(result, LazyImageFile)
        super_gt.assert_not_called()


class LazyThumbnailViewTests(TestCase):
    def test_invalid_payload_returns_404(self):
        response = self.client.get(
            reverse(
                "xprez:sorl_thumbnail_lazy:lazy_thumbnail",
                kwargs={"payload": "garbage", "sig": "badsig"},
            )
        )
        self.assertEqual(response.status_code, 404)

    def test_valid_payload_redirects_to_generated_thumbnail(self):
        payload, sig = encode_thumbnail_payload(
            "images/photo.jpg", "400x300", crop="center"
        )
        thumbnail = Mock(url="/media/cache/photo.webp")
        backend = Mock()
        backend.get_thumbnail.return_value = thumbnail

        with patch("xprez.contrib.sorl_thumbnail.lazy.views.default.backend", backend):
            response = self.client.get(
                reverse(
                    "xprez:sorl_thumbnail_lazy:lazy_thumbnail",
                    kwargs={"payload": payload, "sig": sig},
                )
            )

        self.assertRedirects(
            response, "/media/cache/photo.webp", fetch_redirect_response=False
        )
        backend.get_thumbnail.assert_called_once_with(
            "images/photo.jpg", "400x300", crop="center"
        )

    def test_lazy_backend_uses_generate_thumbnail(self):
        payload, sig = encode_thumbnail_payload("images/photo.jpg", "400x300")
        thumbnail = Mock(url="/media/cache/photo.webp")

        class TestLazyBackend(LazyThumbnailBackendMixin):
            pass

        backend = TestLazyBackend()
        backend.generate_thumbnail = Mock(return_value=thumbnail)
        backend.get_thumbnail = Mock()

        with patch("xprez.contrib.sorl_thumbnail.lazy.views.default.backend", backend):
            response = self.client.get(
                reverse(
                    "xprez:sorl_thumbnail_lazy:lazy_thumbnail",
                    kwargs={"payload": payload, "sig": sig},
                )
            )

        self.assertRedirects(
            response, "/media/cache/photo.webp", fetch_redirect_response=False
        )
        backend.generate_thumbnail.assert_called_once_with(
            "images/photo.jpg", "400x300"
        )
        backend.get_thumbnail.assert_not_called()
