from urllib.parse import parse_qs, urlparse

from django import forms
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _

from xprez.conf import settings
from xprez.models.configs import SectionConfig
from xprez.models.modules import (
    CodeInputModule,
    CodeTemplateModule,
    DownloadsItem,
    DownloadsModule,
    GalleryItem,
    GalleryModule,
    NumbersItem,
    NumbersModule,
    QuoteModule,
    TextModule,
    TextModuleBase,
    VideoModule,
)
from xprez.models.sections import Section
from xprez.utils import import_class


class SectionForm(forms.ModelForm):
    delete = forms.BooleanField(required=False)

    class Meta:
        model = Section
        fields = "__all__"


class SectionConfigForm(forms.ModelForm):
    delete = forms.BooleanField(required=False)

    class Meta:
        model = SectionConfig
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.is_default():
            del self.fields["delete"]


class BaseModuleForm(forms.ModelForm):
    delete = forms.BooleanField(required=False)

    base_module_fields = (
        "position",
        "section",
        "css_class",
        "delete",
    )

    options_fields = ()

    def get_main_fields(self):
        excluded_fields = tuple(self.base_module_fields)
        excluded_fields += self.options_fields

        for field in self.fields:
            if field not in excluded_fields:
                yield self[field]

    def get_options_fields(self):
        for field in self.options_fields:
            yield self[field]

    class Meta:
        fields = "__all__"


class ModuleConfigForm(forms.ModelForm):
    base_module_fields = (
        "visible",
        "colspan",
        "rowspan",
        "vertical_align",
        "horizontal_align",
    )

    def get_extra_fields(self):
        for field in self.fields:
            if field not in self.base_module_fields:
                yield self[field]

    class Meta:
        fields = "__all__"


class TextModuleBaseForm(BaseModuleForm):
    class Meta:
        model = TextModuleBase
        fields = ("text",) + BaseModuleForm.base_module_fields
        widgets = {
            "text": import_class(settings.XPREZ_CK_EDITOR_MODULE_WIDGET)(
                file_upload_dir="ck_editor_uploads"
            )
        }


class TextModuleForm(TextModuleBaseForm):
    options_fields = ("url",) + TextModuleBaseForm.options_fields
    image_clear = forms.BooleanField(required=False)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data.get("image_clear"):
            instance.image = None
        if commit:
            instance.save()
        return instance

    class Meta(TextModuleBaseForm.Meta):
        model = TextModule
        fields = TextModuleBaseForm.Meta.fields + ("image", "url")

        widgets = {"image": forms.FileInput}
        widgets.update(TextModuleBaseForm.Meta.widgets)


class QuoteModuleForm(BaseModuleForm):
    class Meta:
        model = QuoteModule
        fields = (
            "name",
            "job_title",
            "title",
            "quote",
            "image",
        ) + BaseModuleForm.base_module_fields
        widgets = {
            "title": forms.TextInput(attrs={"class": "long"}),
            "quote": forms.Textarea(attrs={"class": "long"}),
        }


class GalleryModuleForm(BaseModuleForm):
    class Meta:
        model = GalleryModule
        fields = (
            "width",
            "columns",
            "divided",
            "crop",
        ) + BaseModuleForm.base_module_fields


GalleryItemFormSet = inlineformset_factory(
    GalleryModule,
    GalleryItem,
    fields=("id", "description", "alt_text", "position"),
    extra=0,
    can_delete=True,
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
        fields = (
            "poster_image",
            "url",
            "width",
        ) + BaseModuleForm.base_module_fields
        widgets = {
            "url": forms.URLInput(attrs={"class": "long"}),
        }


class CodeInputModuleForm(BaseModuleForm):
    class Meta:
        model = CodeInputModule
        fields = ("code",) + BaseModuleForm.base_module_fields


class NumbersModuleForm(BaseModuleForm):
    class Meta:
        model = NumbersModule
        fields = BaseModuleForm.base_module_fields


class NumbersItemForm(forms.ModelForm):
    class Meta:
        model = NumbersItem
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


NumbersItemFormSet = inlineformset_factory(
    NumbersModule,
    NumbersItem,
    form=NumbersItemForm,
    fields=("id", "number", "suffix", "title"),
    max_num=4,
    extra=4,
    can_delete=True,
)


class CodeTemplateModuleForm(BaseModuleForm):
    class Meta:
        model = CodeTemplateModule
        fields = ("template_name",) + BaseModuleForm.base_module_fields


class DownloadsModuleForm(BaseModuleForm):
    class Meta:
        model = DownloadsModule
        fields = ("title",) + BaseModuleForm.base_module_fields
        widgets = {"title": forms.TextInput(attrs={"placeholder": "Files"})}


DownloadsItemFormSet = inlineformset_factory(
    DownloadsModule,
    DownloadsItem,
    fields=("id", "name", "position"),
    extra=0,
    can_delete=True,
)
