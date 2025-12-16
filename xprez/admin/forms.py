try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

from django import forms
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _

from xprez.conf import settings
from xprez.medium_editor.widgets import MediumEditorWidget
from xprez.models.configs import SectionConfig
from xprez.models.modules import (
    Attachment,
    CkEditor,
    CodeInput,
    CodeTemplate,
    DownloadModule,
    FeatureBoxes,
    Gallery,
    GridBoxes,
    MediumEditor,
    Number,
    NumbersModule,
    Photo,
    Quote,
    QuoteModule,
    TextModule,
    TextImage,
    Video,
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
        model = CkEditor
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


class GalleryForm(BaseModuleForm):
    class Meta:
        model = Gallery
        fields = (
            "width",
            "columns",
            "divided",
            "crop",
        ) + BaseModuleForm.base_module_fields


class MediumEditorForm(BaseModuleForm):
    class Meta:
        model = MediumEditor
        fields = (
            "text",
            "box",
            "width",
        ) + BaseModuleForm.base_module_fields
        widgets = {"text": MediumEditorWidget(file_upload_dir="medium_editor_uploads")}


class CkEditorForm(BaseModuleForm):
    class Meta:
        model = CkEditor
        fields = (
            "text",
            "module_centered",
            "box",
            "width",
        ) + BaseModuleForm.base_module_fields
        widgets = {
            "text": import_class(settings.XPREZ_CK_EDITOR_MODULE_WIDGET)(
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


class QuoteModuleForm(BaseModuleForm):
    class Meta:
        model = QuoteModule
        fields = (
            "display_two",
            "title",
            "box",
        ) + BaseModuleForm.base_module_fields


class VideoForm(BaseModuleForm):
    def clean_url(self):
        url = self.cleaned_data["url"]
        parsed_url = urlparse.urlparse(url)
        url_query = urlparse.parse_qs(parsed_url.query)

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
        model = Video
        fields = (
            "poster_image",
            "url",
            "width",
        ) + BaseModuleForm.base_module_fields
        widgets = {
            "url": forms.URLInput(attrs={"class": "long"}),
        }


class CodeInputForm(BaseModuleForm):
    class Meta:
        model = CodeInput
        fields = ("code",) + BaseModuleForm.base_module_fields


class NumbersModuleForm(BaseModuleForm):
    class Meta:
        model = NumbersModule
        fields = BaseModuleForm.base_module_fields


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


class FeatureBoxesForm(BaseModuleForm):
    class Meta:
        model = FeatureBoxes
        fields = (
            "box_1",
            "box_2",
            "box_3",
        ) + BaseModuleForm.base_module_fields
        widgets = {
            "box_1": MediumEditorWidget(mode=MediumEditorWidget.FULL_NO_INSERT_PLUGIN),
            "box_2": MediumEditorWidget(mode=MediumEditorWidget.FULL_NO_INSERT_PLUGIN),
            "box_3": MediumEditorWidget(mode=MediumEditorWidget.FULL_NO_INSERT_PLUGIN),
        }


class CodeTemplateForm(BaseModuleForm):
    class Meta:
        model = CodeTemplate
        fields = ("template_name",) + BaseModuleForm.base_module_fields


class DownloadModuleForm(BaseModuleForm):
    class Meta:
        model = DownloadModule
        fields = ("title",) + BaseModuleForm.base_module_fields
        widgets = {"title": forms.TextInput(attrs={"placeholder": "Files"})}


class TextImageForm(BaseModuleForm):
    class Meta:
        model = TextImage
        fields = (
            "image",
            "text",
            "image_alignment",
        ) + BaseModuleForm.base_module_fields
        widgets = {
            "text": import_class(settings.XPREZ_TEXT_IMAGE_MODULE_WIDGET)(),
        }


class GridBoxesForm(BaseModuleForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ckeditor_widget_tpl = import_class(
            settings.XPREZ_GRID_BOXES_MODULE_WIDGET
        )()

    class Meta:
        model = GridBoxes
        fields = (
            "columns",
            "margin",
            "width",
            "text_size",
            "padded",
            "module_centered",
            "image_sizing",
            "image_max_width",
            "boxes_filled",
            "border",
            "boxes",
        ) + BaseModuleForm.base_module_fields


AttachmentFormSet = inlineformset_factory(
    DownloadModule,
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
    QuoteModule,
    Quote,
    form=QuoteForm,
    fields=("id", "name", "job_title", "title", "quote", "image"),
    max_num=2,
    can_delete=True,
)
NumberFormSet = inlineformset_factory(
    NumbersModule,
    Number,
    form=NumberForm,
    fields=("id", "number", "suffix", "title"),
    max_num=4,
    extra=4,
    can_delete=True,
)
