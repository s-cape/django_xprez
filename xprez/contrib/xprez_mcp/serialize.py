"""Model values and form field schemas as JSON."""

import datetime
import decimal

from django import forms
from django.core.exceptions import FieldDoesNotExist
from django.db import models

from xprez.admin.forms import ModuleForm, PositionFormMixin
from xprez.ck_editor.widgets import CkEditorWidgetBase

from .html import text_rules


def model_values(instance, names):
    """``{name: value}`` of ``names`` on ``instance`` as JSON values."""
    opts = instance._meta
    result = {}
    for name in names:
        try:
            field = opts.get_field(name)
        except FieldDoesNotExist:
            continue
        result[name] = field_value(instance, field)
    return result


def field_value(instance, field):
    if isinstance(field, models.FileField):
        file = getattr(instance, field.name)
        if not file:
            return None
        try:
            url = file.url
        except ValueError:
            url = None
        return {"url": url, "path": file.name}
    if field.many_to_many:
        return [related.pk for related in getattr(instance, field.name).all()]
    if field.is_relation:
        return getattr(instance, field.attname)
    value = field.value_from_object(instance)
    if isinstance(value, (datetime.date, datetime.time)):
        return value.isoformat()
    if isinstance(value, decimal.Decimal):
        return str(value)
    return value


def form_field_names(form_class):
    """The fields of an admin form an MCP client may set: not the form's
    ``system_fields``, nor what the move tools set (position, section)."""
    excluded = set(getattr(form_class, "system_fields", ()))
    if issubclass(form_class, PositionFormMixin):
        excluded.add("position")
    if issubclass(form_class, ModuleForm):
        excluded.update(ModuleForm.base_module_fields)
    return [name for name in form_class.base_fields if name not in excluded]


def form_schema(form_class):
    """``{name: JSON schema}`` of the settable fields of ``form_class``."""
    return {
        name: field_schema(form_class.base_fields[name])
        for name in form_field_names(form_class)
    }


def field_schema(field):
    schema = _base_schema(field)
    description = " ".join(
        str(text) for text in (field.label, field.help_text) if text
    ).strip()
    if description:
        schema["description"] = description
    if not field.required:
        schema["required"] = False
    return schema


def _base_schema(field):
    if isinstance(field, forms.FileField):
        return {"type": "file"}
    if isinstance(field, forms.ModelMultipleChoiceField):
        return {"type": "array", "items": {"type": "integer"}}
    if isinstance(field, forms.ModelChoiceField):
        return {"type": "integer", "description": "id"}
    if isinstance(field, forms.ChoiceField):
        values = [_choice_value(value) for value, _label in _flat_choices(field)]
        return {"enum": values}
    if isinstance(field, forms.BooleanField):
        return {"type": "boolean"}
    if isinstance(field, forms.IntegerField):
        schema = {"type": "integer"}
        _add_bounds(schema, field)
        return schema
    if isinstance(field, (forms.FloatField, forms.DecimalField)):
        schema = {"type": "number"}
        _add_bounds(schema, field)
        return schema
    if isinstance(field, forms.DateTimeField):
        return {"type": "string", "format": "date-time"}
    if isinstance(field, forms.DateField):
        return {"type": "string", "format": "date"}
    schema = {"type": "string"}
    if isinstance(field.widget, CkEditorWidgetBase):
        schema["format"] = "html"
        schema["html"] = text_rules(field.widget).as_dict()
    if getattr(field, "max_length", None):
        schema["maxLength"] = field.max_length
    return schema


def _flat_choices(field):
    for value, label in field.choices:
        if isinstance(label, (list, tuple)):  # optgroup
            yield from label
        else:
            yield value, label


def _choice_value(value):
    return "" if value is None else value


def _add_bounds(schema, field):
    if field.min_value is not None:
        schema["minimum"] = field.min_value
    if field.max_value is not None:
        schema["maximum"] = field.max_value
