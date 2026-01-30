from urllib.parse import parse_qs, urlparse

from django import forms
from django.db import models
from django.utils.translation import gettext_lazy as _

from xprez.admin.forms import BaseModuleForm
from xprez.models.modules import Module


class VideoModule(Module):
    TYPE_CHOICES = (
        ("youtube", "YouTube"),
        ("vimeo", "Vimeo"),
    )
    admin_template_name = "xprez/admin/modules/video.html"
    front_template_name = "xprez/modules/video.html"
    icon_template_name = "xprez/admin/icons/modules/video.html"
    form_class = "xprez.modules.video.VideoForm"

    poster_image = models.ImageField(upload_to="video", null=True, blank=True)
    url = models.URLField()
    # width = models.CharField(
    #     max_length=50, choices=Module.SIZE_CHOICES, default=Module.SIZE_FULL
    # )
    video_type = models.CharField(choices=TYPE_CHOICES, max_length=50, editable=False)
    video_id = models.CharField(max_length=200, editable=False)

    def save_admin_form(self, request):
        inst = self.admin_form.save(commit=False)
        inst.video_type = self.admin_form.video_type
        inst.video_id = self.admin_form.video_id
        inst.save()

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


class VideoForm(BaseModuleForm):
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
