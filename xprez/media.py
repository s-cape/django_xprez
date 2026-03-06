from django.forms import Media
from django.templatetags.static import static
from django.utils.html import format_html

from xprez.conf import settings


class PrefixableMedia(Media):
    """Media with absolute_path overridden for XPREZ_USE_ABSOLUTE_URI."""

    @staticmethod
    def from_media(media):
        prefixable = PrefixableMedia()
        prefixable._css_lists = media._css_lists
        prefixable._js_lists = media._js_lists
        return prefixable

    def absolute_path(self, path):
        absolute_path = super().absolute_path(path)
        if settings.XPREZ_USE_ABSOLUTE_URI and not path.startswith(
            ("http://", "https://", "//")
        ):
            return "{}{}".format(settings.XPREZ_BASE_URL, absolute_path)
        else:
            return absolute_path


class MediaCollectorBase:
    """Base for collecting Admin/Front media from module classes."""

    def get_media(self):
        raise NotImplementedError

    def get_module_classes(self):
        from xprez.registry import module_registry

        return module_registry.allowed_module_classes()

    @staticmethod
    def _preprocess_js(js_specs):
        """(path, 'module') -> script tag; strings unchanged."""
        out = []
        for spec in js_specs:
            is_module = (
                isinstance(spec, (list, tuple))
                and len(spec) == 2
                and spec[1] == "module"
            )
            out += [
                format_html('<script type="module" src="{}"></script>', static(spec[0]))
                if is_module
                else spec,
            ]
        return tuple(out)

    @staticmethod
    def _preprocess(media):
        return Media(
            js=MediaCollectorBase._preprocess_js(media._js),
            css=media._css,
        )

    def _collect(self, media_class_name):
        media = Media()
        for module_class in self.get_module_classes():
            data = getattr(module_class, media_class_name)
            module_media = Media(
                css=getattr(data, "css", {}), js=getattr(data, "js", [])
            )
            media += self._preprocess(module_media)
        return media


class AdminMediaCollector(MediaCollectorBase):
    """Admin media for XprezAdminMixin."""

    def get_media(self):
        common = self._preprocess(
            Media(
                js=settings.XPREZ_ADMIN_MEDIA_JS,
                css=settings.XPREZ_ADMIN_MEDIA_CSS,
            )
        )
        return common + self._collect("AdminMedia")


class FrontendMediaCollector(MediaCollectorBase):
    """Collects front media; has container for future per-container scoping."""

    def __init__(self, container=None):
        self.container = container

    def get_media(self):
        common = self._preprocess(
            Media(
                js=settings.XPREZ_FRONT_MEDIA_JS,
                css=settings.XPREZ_FRONT_MEDIA_CSS,
            )
        )
        return PrefixableMedia.from_media(common + self._collect("FrontMedia"))
