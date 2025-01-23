try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

from django import forms
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _

from .conf import settings
from .medium_editor.widgets import MediumEditorWidget
from .models import (
    Attachment,
    CkEditor,
    CodeInput,
    CodeTemplate,
    DownloadContent,
    FeatureBoxes,
    Gallery,
    GridBoxes,
    MediumEditor,
    Number,
    NumbersContent,
    Photo,
    Quote,
    QuoteContent,
    TextImage,
    Video,
)
from .utils import import_class


class BaseContentForm(forms.ModelForm):
    base_content_fields = (
        "position",
        "visible",
        "css_class",
        "margin_bottom",
        "padding_top",
        "padding_bottom",
        "alternate_color",
        "background_color",
    )

    def main_fields(self):
        excluded_fields = tuple(self.base_content_fields)
        excluded_fields += getattr(self._meta, "options_fields", ())

        for field in self.fields:
            if field not in excluded_fields:
                yield self[field]

    class Meta:
        options_fields = tuple()
        fields = "__all__"


class GalleryForm(BaseContentForm):
    class Meta:
        model = Gallery
        fields = (
            "width",
            "columns",
            "divided",
            "crop",
        ) + BaseContentForm.base_content_fields


class MediumEditorForm(BaseContentForm):
    class Meta:
        model = MediumEditor
        fields = (
            "text",
            "box",
            "width",
        ) + BaseContentForm.base_content_fields
        widgets = {"text": MediumEditorWidget(file_upload_dir="medium_editor_uploads")}


class CkEditorForm(BaseContentForm):
    class Meta:
        model = CkEditor
        fields = (
            "text",
            "content_centered",
            "box",
            "width",
        ) + BaseContentForm.base_content_fields
        widgets = {
            "text": import_class(settings.XPREZ_CK_EDITOR_CONTENT_WIDGET)(
                file_upload_dir="ck_editor_uploads"
            )
        }


class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ("id", "name", "job_title", "title", "quote", "image")
        widgets = {
            "title": forms.TextInput(attrs={"class": "long"}),
            "quote": forms.Textarea(attrs={"class": "long"}),
        }


class QuoteContentForm(BaseContentForm):
    class Meta:
        model = QuoteContent
        fields = (
            "display_two",
            "title",
            "box",
        ) + BaseContentForm.base_content_fields


class VideoForm(BaseContentForm):
    def clean_url(self):
        url = self.cleaned_data["url"]
        parsed_url = urlparse.urlparse(url)
        url_query = urlparse.parse_qs(parsed_url.query)

        if "youtube" in url:
            try:
                self.video_id = url_query.get("v")[0]
            except (KeyError, TypeError):
                raise forms.ValidationError(_("Error in parsing video ID from youtube"))
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
        model = Video
        fields = (
            "poster_image",
            "url",
            "width",
        ) + BaseContentForm.base_content_fields
        widgets = {
            "url": forms.URLInput(attrs={"class": "long"}),
        }


class CodeInputForm(BaseContentForm):
    class Meta:
        model = CodeInput
        fields = ("code",) + BaseContentForm.base_content_fields


class NumbersContentForm(BaseContentForm):
    class Meta:
        model = NumbersContent
        fields = BaseContentForm.base_content_fields


class NumberForm(forms.ModelForm):
    class Meta:
        model = Number
        widgets = {
            "number": forms.NumberInput(attrs={"class": "short"}),
            "suffix": forms.TextInput(attrs={"class": "short"}),
        }
        fields = (
            "id",
            "number",
            "suffix",
            "title",
        )


class FeatureBoxesForm(BaseContentForm):
    class Meta:
        model = FeatureBoxes
        fields = (
            "box_1",
            "box_2",
            "box_3",
        ) + BaseContentForm.base_content_fields
        widgets = {
            "box_1": MediumEditorWidget(mode=MediumEditorWidget.FULL_NO_INSERT_PLUGIN),
            "box_2": MediumEditorWidget(mode=MediumEditorWidget.FULL_NO_INSERT_PLUGIN),
            "box_3": MediumEditorWidget(mode=MediumEditorWidget.FULL_NO_INSERT_PLUGIN),
        }


class CodeTemplateForm(BaseContentForm):
    class Meta:
        model = CodeTemplate
        fields = ("template_name",) + BaseContentForm.base_content_fields


class DownloadContentForm(BaseContentForm):
    class Meta:
        model = DownloadContent
        fields = ("title",) + BaseContentForm.base_content_fields
        widgets = {"title": forms.TextInput(attrs={"placeholder": "Files"})}


class TextImageForm(BaseContentForm):
    class Meta:
        model = TextImage
        fields = (
            "image",
            "text",
            "image_alignment",
        ) + BaseContentForm.base_content_fields
        widgets = {
            "text": import_class(settings.XPREZ_TEXT_IMAGE_CONTENT_WIDGET)(),
        }


class GridBoxesForm(BaseContentForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ckeditor_widget_tpl = import_class(
            settings.XPREZ_GRID_BOXES_CONTENT_WIDGET
        )()

    class Meta:
        model = GridBoxes
        fields = (
            "columns",
            "margin",
            "width",
            "text_size",
            "padded",
            "content_centered",
            "image_sizing",
            "image_max_width",
            "boxes_filled",
            "border",
            "boxes",
        ) + BaseContentForm.base_content_fields


AttachmentFormSet = inlineformset_factory(
    DownloadContent,
    Attachment,
    fields=("id", "name", "position"),
    extra=0,
    can_delete=True,
)
PhotoFormSet = inlineformset_factory(
    Gallery,
    Photo,
    fields=("id", "description", "alt_text", "position"),
    extra=0,
    can_delete=True,
)
QuoteFormSet = inlineformset_factory(
    QuoteContent,
    Quote,
    form=QuoteForm,
    fields=("id", "name", "job_title", "title", "quote", "image"),
    max_num=2,
    can_delete=True,
)
NumberFormSet = inlineformset_factory(
    NumbersContent,
    Number,
    form=NumberForm,
    fields=("id", "number", "suffix", "title"),
    max_num=4,
    extra=4,
    can_delete=True,
)
