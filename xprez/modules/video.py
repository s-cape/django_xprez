import re
from functools import lru_cache

from django import forms
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from xprez import constants
from xprez.admin.forms import ModuleForm
from xprez.conf import settings
from xprez.models.mixins.responsive_image import ResponsiveImageMixin
from xprez.models.modules import Module
from xprez.utils import import_class


class VideoProviderBase:
    """Base for video URL providers. Set patterns (list of str) or override."""

    key = ""
    example = ""
    patterns = []  # list of str, each with (?P<video_id>...) group

    @cached_property
    def _compiled_patterns(self):
        return [re.compile(p) for p in self.patterns]

    def get_id(self, url):
        """Return video_id if this provider handles the URL, else None."""
        for pattern in self._compiled_patterns:
            match = pattern.search(url)
            if match:
                return match.group("video_id")
        return None

    @property
    def embed_template_name(self):
        return f"xprez/includes/video_embeds/{self.key}.html"


class YouTubeVideoProvider(VideoProviderBase):
    key = "youtube"
    example = "https://www.youtube.com/watch?v=TpQlyUjp3vM"
    patterns = [
        r"https?://(?:www\.|m\.)?youtube\.com/watch\?.*v=(?P<video_id>[^&#]+)",
        r"https?://youtu\.be/(?P<video_id>[^/?&#]+)",
        r"https?://(?:www\.|m\.)?youtube\.com/embed/(?P<video_id>[^/?&#]+)",
    ]


class VimeoVideoProvider(VideoProviderBase):
    key = "vimeo"
    example = "https://vimeo.com/210073083"
    patterns = [
        r"https?://(?:www\.|player\.)?vimeo\.com/(?:video/)?(?P<video_id>\d+)",
    ]


@lru_cache(maxsize=None)
def get_video_providers():
    return [import_class(path)() for path in settings.XPREZ_VIDEO_PROVIDERS]


class VideoModule(ResponsiveImageMixin, Module):
    front_cacheable = True
    front_template_name = "xprez/modules/video.html"
    admin_template_name = "xprez/admin/modules/video.html"
    admin_form_class = "xprez.modules.video.VideoForm"
    admin_icon_template_name = "xprez/shared/icons/modules/video.html"

    poster_image = models.ImageField(upload_to="video", null=True, blank=True)
    url = models.URLField()
    video_type = models.CharField(max_length=50, editable=False)
    video_id = models.CharField(max_length=200, editable=False)

    class Meta:
        verbose_name = "Video"

    def get_image_field(self):
        return self.poster_image

    def get_aspect_ratio(self):
        num, den = constants.ASPECT_RATIO_16_9.split("/")
        return int(num), int(den)

    def get_video_provider(self):
        for provider in get_video_providers():
            if provider.key == self.video_type:
                return provider
        return None

    def get_embed_template_name(self):
        provider = self.get_video_provider()
        return provider.embed_template_name if provider else None

    def render_front(self, context):
        if self.url:
            return super().render_front(context)
        else:
            return ""

    class FrontMedia:
        js = (
            "xprez/js/video.js",
            "//www.youtube.com/iframe_api",
            "//player.vimeo.com/api/player.js",
        )


class VideoForm(ModuleForm):
    def clean_url(self):
        url = self.cleaned_data["url"]
        providers = get_video_providers()
        for provider in providers:
            video_id = provider.get_id(url)
            if video_id is None:
                continue
            self.video_type = provider.key
            self.video_id = video_id
            return url
        examples = ", ".join(f"{p.example}" for p in providers if p.example)
        raise forms.ValidationError(
            _("Unsupported Video URL. Examples: %(examples)s") % {"examples": examples}
        )

    def save(self, commit=True):
        inst = super().save(commit=False)
        inst.video_type = self.video_type
        inst.video_id = self.video_id
        if commit:
            inst.save()
        return inst

    class Meta:
        model = VideoModule
        fields = "__all__"
