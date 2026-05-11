from django.core.cache import cache

from xprez.conf import settings


class FrontCacheMixin:
    """Frontend render caching by fixed key per object; invalidate via delete."""

    front_cacheable = False

    def front_cache_key(self):
        return f"xprez:f:{self.KEY}:{self.pk}"

    @staticmethod
    def _front_cache_set(key, value):
        """Set cache; XPREZ_FRONT_CACHE_TIMEOUT None = use backend default."""
        timeout = settings.XPREZ_FRONT_CACHE_TIMEOUT
        if timeout is not None:
            cache.set(key, value, timeout=timeout)
        else:
            cache.set(key, value)

    def _get_front_cached(self, key, render_fn, store=True):
        """Return cache hit or render via render_fn(), optionally storing. Bypasses cache when disabled."""
        if settings.XPREZ_FRONT_CACHE_ENABLED is False:
            return render_fn()
        else:
            cached = cache.get(key)
            if cached is not None:
                return cached
            else:
                result = render_fn()
                if store:
                    self._front_cache_set(key, result)
                return result

    def render_front_cached(self, context):
        return self._get_front_cached(
            self.front_cache_key(),
            lambda: self.render_front(context),
            store=self.front_cacheable,
        )

    def invalidate_front_cache(self):
        cache.delete(self.front_cache_key())

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.pk:
            self.invalidate_front_cache()


class ContentFrontCacheMixin(FrontCacheMixin):
    """Adds CSS cached methods and cache invalidation for Section/Module."""

    def _front_css_vars_cache_key(self):
        return f"xprez:css:vars:{self.KEY}:{self.pk}"

    def _front_css_classes_cache_key(self):
        return f"xprez:css:classes:{self.KEY}:{self.pk}"

    def front_css_variables_cached(self):
        return self._get_front_cached(
            self._front_css_vars_cache_key(),
            self.render_css_variables,
        )

    def front_css_classes_cached(self):
        return self._get_front_cached(
            self._front_css_classes_cache_key(),
            self.render_css_classes,
        )

    def invalidate_front_cache(self):
        cache.delete(self._front_css_vars_cache_key())
        cache.delete(self._front_css_classes_cache_key())
        super().invalidate_front_cache()
