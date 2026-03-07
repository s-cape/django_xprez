from django.core.cache import cache

from xprez.conf import settings


class FrontCacheMixin:
    """Version-bump-based frontend render caching."""

    front_cacheable = False

    def get_front_version_cache_key(self):
        return f"xprez:v:{self.KEY}:{self.pk}"

    def get_front_cache_version(self):
        return cache.get(self.get_front_version_cache_key()) or 0

    def bump_front_cache_version(self):
        key = self.get_front_version_cache_key()
        try:
            cache.incr(key)
        except ValueError:
            cache.set(key, 1, timeout=None)

    def front_cache_key(self):
        return f"xprez:r:{self.KEY}:{self.pk}:{self.get_front_cache_version()}"

    @staticmethod
    def _front_cache_set(key, value):
        """Set cache; XPREZ_FRONT_CACHE_TIMEOUT None = use backend default."""
        timeout = settings.XPREZ_FRONT_CACHE_TIMEOUT
        if timeout is not None:
            cache.set(key, value, timeout=timeout)
        else:
            cache.set(key, value)

    def render_front_cached(self, context):
        if settings.XPREZ_FRONT_CACHE_ENABLED is False:
            return self.render_front(context)
        else:
            key = self.front_cache_key()
            result = cache.get(key)
            if result is not None:
                return result
            else:
                result = self.render_front(context)
                if self.front_cacheable:
                    self._front_cache_set(key, result)
                return result

    def invalidate_front_cache(self):
        self.bump_front_cache_version()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.pk:
            self.invalidate_front_cache()


class ContentFrontCacheMixin(FrontCacheMixin):
    """Adds CSS cached methods and cache invalidation for Section/Module."""

    def front_css_variables_cached(self):
        if settings.XPREZ_FRONT_CACHE_ENABLED is False:
            return self.render_css_variables()
        else:
            key = f"xprez:css:vars:{self.KEY}:{self.pk}"
            result = cache.get(key)
            if result is not None:
                return result
            else:
                result = self.render_css_variables()
                self._front_cache_set(key, result)
                return result

    def front_css_classes_cached(self):
        if settings.XPREZ_FRONT_CACHE_ENABLED is False:
            return self.render_css_classes()
        else:
            key = f"xprez:css:classes:{self.KEY}:{self.pk}"
            result = cache.get(key)
            if result is not None:
                return result
            else:
                result = self.render_css_classes()
                self._front_cache_set(key, result)
                return result

    def invalidate_front_cache(self):
        cache.delete(f"xprez:css:vars:{self.KEY}:{self.pk}")
        cache.delete(f"xprez:css:classes:{self.KEY}:{self.pk}")
        super().invalidate_front_cache()
