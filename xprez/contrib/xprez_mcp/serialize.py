"""Model values and form field schemas as JSON."""

import datetime
import decimal

from django.core.exceptions import FieldDoesNotExist
from django.db import models
from xprez_mcp.core.files import file_argument
from xprez_mcp.core.schema import annotation_schema
from xprez_mcp.providers.fields import field_annotation

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
    """The fields of an admin form an MCP client may set: its model fields,
    without the form's ``system_fields`` and what the move tools set
    (position, section)."""
    excluded = set(getattr(form_class, "system_fields", ()))
    if issubclass(form_class, PositionFormMixin):
        excluded.add("position")
    if issubclass(form_class, ModuleForm):
        excluded.update(ModuleForm.base_module_fields)
    model = form_class._meta.model
    return [
        name
        for name in form_class.base_fields
        if name not in excluded and (model is None or has_field(model, name))
    ]


def form_schema(form_class, file_sources):
    """``{name: JSON schema}`` of the settable fields of ``form_class``, from
    their model fields as django-xprez-mcp types them. File fields take
    ``file_sources``; without any they cannot be set and are left out."""
    model = form_class._meta.model
    schema = {}
    for name in form_field_names(form_class):
        model_field = model._meta.get_field(name)
        if isinstance(model_field, models.FileField) and not file_sources:
            continue
        schema[name] = field_schema(
            form_class.base_fields[name], model_field, file_sources
        )
    return schema


def field_schema(form_field, model_field, file_sources):
    if isinstance(model_field, models.FileField):
        annotation = file_argument(file_sources, nullable=model_field.blank)
    else:
        annotation = field_annotation(model_field)
    schema = dict(annotation_schema(annotation))
    description = " ".join(
        str(text) for text in (form_field.label, form_field.help_text) if text
    )
    if description:
        schema["description"] = description
    if not form_field.required:
        schema["required"] = False
    if isinstance(form_field.widget, CkEditorWidgetBase):
        schema["format"] = "html"
        schema["html"] = text_rules(form_field.widget).as_dict()
    return schema


def has_field(model, name):
    try:
        model._meta.get_field(name)
    except FieldDoesNotExist:
        return False
    return True
