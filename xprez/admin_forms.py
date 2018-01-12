try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

from django.utils.translation import ugettext_lazy as _
from django import forms
from django.forms import inlineformset_factory
from .models import (
    Gallery, MediumEditor, Photo, QuoteContent, Quote, Video, CodeInput,
    NumbersContent, Number, FeatureBoxes, CodeTemplate, DownloadContent, Attachment
)
from .medium_editor.widgets import MediumEditorWidget


class BaseContentForm(forms.ModelForm):
    pass
    # delete = forms.BooleanField(initial=False, required=False)

    # def should_be_deleted(self):
    #     return self.data.get(str(self.prefix)+'-delete') == 'on'

    # def is_valid(self):
    #     if self.should_be_deleted():
    #         return True
    #     return super(BaseContentForm, self).is_valid()


class GalleryForm(BaseContentForm):
    class Meta:
        model = Gallery
        fields = ('width', 'columns', 'divided', 'crop', 'position')


class MediumEditorForm(BaseContentForm):
    class Meta:
        model = MediumEditor
        fields = ('text', 'position', 'box', 'width', 'css_class')
        widgets = {
            'text': MediumEditorWidget(file_upload_dir='medium_editor_uploads')
        }


class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ('id', 'name', 'job_title', 'title', 'quote', 'image')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'long'}),
            'quote': forms.Textarea(attrs={'class': 'long'}),
        }


class QuoteContentForm(BaseContentForm):
    class Meta:
        model = QuoteContent
        fields = ('display_two', 'position', 'title', 'box')


class VideoForm(BaseContentForm):

    def clean_url(self):
        url = self.cleaned_data['url']
        parsed_url = urlparse.urlparse(url)
        url_query = urlparse.parse_qs(parsed_url.query)

        if 'youtube' in url:
            try:
                self.video_id = url_query.get('v')[0]
            except (KeyError, TypeError):
                raise forms.ValidationError(_('Error in parsing video ID from youtube'))
            self.video_type = 'youtube'
        elif 'vimeo' in url:
            self.video_id = url.split('/')[-1]
            self.video_type = 'vimeo'
        else:
            raise forms.ValidationError(_('Unsupported Video URL, it should be in format: "https://www.youtube.com/watch?v=nNGBxXN7QC0" or "https://vimeo.com/210073083" '))
        return url

    class Meta:
        model = Video
        fields = ('poster_image', 'url', 'position', 'width')
        widgets = {
            'url': forms.URLInput(attrs={'class': 'long'}),
        }


class CodeInputForm(BaseContentForm):
    class Meta:
        model = CodeInput
        fields = ('code', 'position')


class NumbersContentForm(BaseContentForm):
    class Meta:
        model = NumbersContent
        fields = ('position', )


class NumberForm(forms.ModelForm):
    class Meta:
        model = Number
        widgets = {
            'number': forms.NumberInput(attrs={'class': 'short'}),
            'suffix': forms.TextInput(attrs={'class': 'short'}),
        }
        fields = ('id', 'number', 'suffix', 'title')


class FeatureBoxesForm(BaseContentForm):
    class Meta:
        model = FeatureBoxes
        fields = ('position', 'box_1', 'box_2', 'box_3')
        widgets = {
            'box_1': MediumEditorWidget(simple=True),
            'box_2': MediumEditorWidget(simple=True),
            'box_3': MediumEditorWidget(simple=True),
        }


class CodeTemplateForm(BaseContentForm):

    class Meta:
        model = CodeTemplate
        fields = ('position', 'template_name', )


class DownloadContentForm(BaseContentForm):
    class Meta:
        model = DownloadContent
        fields = ('position', 'title')
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Files'})
        }


AttachmentFormSet = inlineformset_factory(DownloadContent, Attachment, fields=('id', 'name', 'position'), extra=0, can_delete=True)
PhotoFormSet = inlineformset_factory(Gallery, Photo, fields=('id', 'description', 'position'), extra=0, can_delete=True)
QuoteFormSet = inlineformset_factory(QuoteContent, Quote, form=QuoteForm, fields=('id', 'name', 'job_title', 'title', 'quote', 'image'), max_num=2, can_delete=True)
NumberFormSet = inlineformset_factory(NumbersContent, Number, form=NumberForm, fields=('id', 'number', 'suffix', 'title'), max_num=4, extra=4, can_delete=True)