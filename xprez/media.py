from django.forms import Media

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
            return f"{settings.XPREZ_BASE_URL}{absolute_path}"
        return absolute_path


class MediaCollectorBase:
    """Base for collecting Admin/Front media from module classes."""

    def get_media(self):
        raise NotImplementedError

    def get_module_classes(self):
        from xprez.registry import module_registry

        return module_registry.allowed_module_classes()

    def _collect(self, media_class_name):
        media = Media()
        for module_class in self.get_module_classes():
            data = getattr(module_class, media_class_name)
            module_media = Media(
                css=getattr(data, "css", {}), js=getattr(data, "js", [])
            )
            media += module_media
        return media


class AdminMediaCollector(MediaCollectorBase):
    """Admin media for XprezAdminMixin."""

    def get_media(self):
        common = Media(
            js=settings.XPREZ_ADMIN_MEDIA_JS,
            css=settings.XPREZ_ADMIN_MEDIA_CSS,
        )
        return common + self._collect("AdminMedia")


class FrontendMediaCollector(MediaCollectorBase):
    """Collects front media; has container for future per-container scoping."""

    def __init__(self, container=None):
        self.container = container

    def get_media(self):
        media = Media(
            js=settings.XPREZ_FRONT_MEDIA_JS,
            css=settings.XPREZ_FRONT_MEDIA_CSS,
        ) + self._collect("FrontMedia")
        return PrefixableMedia.from_media(media)
