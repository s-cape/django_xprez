from django import forms

from .models import CodeSnippet
from xprez.admin_forms import BaseContentForm


class CodeSnippetForm(BaseContentForm):
    class Meta:
        fields = ('position', 'title', 'lang', 'code', 'visible')
        model = CodeSnippet
        widgets = {
            'code': forms.Textarea(attrs={'class': 'js-code-snippet wide', 'cols': 100,})
        }
