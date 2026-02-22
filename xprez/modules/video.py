from urllib.parse import parse_qs, urlparse

from django import forms
from django.db import models
from django.utils.translation import gettext_lazy as _

from xprez.admin.forms import ModuleForm
from xprez.conf import settings
from xprez.models.modules import Module
from xprez.models.mixins.responsive_image import ResponsiveImageMixin


class VideoModule(ResponsiveImageMixin, Module):
    front_template_name = "xprez/modules/video.html"
    admin_template_name = "xprez/admin/modules/video.html"
    admin_form_class = "xprez.modules.video.VideoForm"
    admin_icon_template_name = "xprez/admin/icons/modules/video.html"

    poster_image = models.ImageField(upload_to="video", null=True, blank=True)
    url = models.URLField()
    TYPE_CHOICES = (
        ("youtube", "YouTube"),
        ("vimeo", "Vimeo"),
    )
    video_type = models.CharField(choices=TYPE_CHOICES, max_length=50, editable=False)
    video_id = models.CharField(max_length=200, editable=False)

    def save_admin_form(self, request):
        inst = self.admin_form.save(commit=False)
        inst.video_type = self.admin_form.video_type
        inst.video_id = self.admin_form.video_id
        inst.save()

    def get_breakpoint_ranges(self):
        """Yield single-column ranges for all breakpoints."""
        breakpoints = settings.XPREZ_BREAKPOINTS
        bp_ids = list(breakpoints)
        for index, bp_id in enumerate(bp_ids):
            min_width = breakpoints[bp_id]["min_width"]
            next_min_width = (
                breakpoints[bp_ids[index + 1]]["min_width"]
                if index + 1 < len(bp_ids)
                else None
            )
            yield min_width, 1, next_min_width

    def get_image_field(self):
        return self.poster_image

    def get_aspect_ratio(self):
        return (16, 9)

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
        parsed_url = urlparse(url)
        url_query = parse_qs(parsed_url.query)

        if "youtube" in url:
            try:
                self.video_id = url_query.get("v")[0]
            except (KeyError, TypeError) as e:
                raise forms.ValidationError(
                    _("Error in parsing video ID from youtube")
                ) from e
            self.video_type = "youtube"
        elif "vimeo" in url:
            self.video_id = url.split("/")[-1]
            self.video_type = "vimeo"
        else:
            raise forms.ValidationError(
                _(
                    'Unsupported Video URL, it should be in format: "https://www.youtube.com/watch?v=nNGBxXN7QC0" or "https://vimeo.com/210073083" '
                )
            )
        return url

    class Meta:
        model = VideoModule
        fields = "__all__"
        # widgets = {
        #     "url": forms.URLInput(attrs={"class": "long"}),
        # }
