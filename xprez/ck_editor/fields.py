from django.db import models
from django.utils.html import strip_tags

from . import widgets


class HtmlField(models.TextField):
    def clean(self, *args, **kwargs):
        value = super().clean(*args, **kwargs)
        if value and not strip_tags(value):
            value = ""

        return value


class CkEditorFieldSimple(HtmlField):
    def formfield(self, **kwargs):
        kwargs["widget"] = widgets.CkEditorWidgetSimple
        return super().formfield(**kwargs)


class CkEditorFieldFullNoInsertPlugin(HtmlField):
    def formfield(self, **kwargs):
        kwargs["widget"] = widgets.CkEditorWidgetNoInsertPlugin
        return super().formfield(**kwargs)


class CkEditorFieldFull(HtmlField):
    def formfield(self, **kwargs):
        kwargs["widget"] = widgets.CkEditorWidgetFull
        return super().formfield(**kwargs)


CkEditorField = CkEditorFieldFull
