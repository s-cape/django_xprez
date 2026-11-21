"""Writes through the admin's forms.

Each write builds the data the admin change page would post for the object:
the current value of every field, with the values sent over MCP on top (a
``ModelForm`` reads a missing field as empty). The objects' own
``build_admin_form`` / ``is_admin_form_valid`` / ``save_admin_form`` then
validate and save it, so the admin's rules hold over MCP too.
"""

from django import forms
from django.db import models
from django.http import QueryDict
from django.utils.datastructures import MultiValueDict
from xprez_mcp import InvalidArguments, ToolError
from xprez_mcp.providers.model import form_error

from xprez.ck_editor.widgets import CkEditorWidgetBase
from xprez.conf import settings

from .html import clean_html, text_rules
from .serialize import form_field_names


def write(xprez_admin, request, obj, fields, configs):
    """Validate and save ``fields`` and ``configs`` on a section or module
    through its own admin form; returns notes on what was changed in the
    values sent (cleaned HTML). A section's modules and a module's items are
    left as they are: they have their own tools."""
    prepare_configs(obj, configs)
    obj.build_admin_form(xprez_admin)
    form = obj.admin_form
    data = QueryDict(mutable=True)
    put_form(data, form)
    notes = put_values(data, form, fields)
    notes += put_configs(data, f"{obj.KEY}-config-id", form.xprez_configs, configs)
    if hasattr(obj, "items_attribute"):
        data.setlist(f"{obj.instance_key}-item-id", [])
    obj.build_admin_form(xprez_admin, data=data, files=MultiValueDict())
    if hasattr(obj.admin_form, "xprez_modules"):
        obj.admin_form.xprez_modules = []
    if not obj.is_admin_form_valid():
        raise invalid(obj.admin_form)
    obj.save_admin_form(request)
    return notes


def prepare_configs(parent, configs):
    """Check the breakpoints of ``configs`` and create the configs they add."""
    for breakpoint, values in configs.items():
        if breakpoint not in settings.XPREZ_BREAKPOINTS:
            raise InvalidArguments(
                f"configs: breakpoint {breakpoint} does not exist; "
                f"use one of {sorted(settings.XPREZ_BREAKPOINTS)}."
            )
        if values is None:
            if breakpoint == 0:
                raise InvalidArguments(
                    "configs: the base config (0) cannot be removed."
                )
        else:
            parent.get_or_create_config(breakpoint)


def put_configs(data, id_key, parent_configs, configs):
    data.setlist(id_key, [str(config.pk) for config in parent_configs])
    notes = []
    for config in parent_configs:
        form = config.admin_form
        put_form(data, form)
        values = configs.get(config.css_breakpoint, {})
        if values is None:
            data[form.add_prefix("delete")] = "on"
        else:
            label = f"configs.{config.css_breakpoint}"
            notes += put_values(data, form, values, label=label)
    return notes


def put_form(data, form):
    """The current values of ``form``'s fields, as the admin page posts them."""
    for name, field in form.fields.items():
        if name == "delete" or isinstance(field, forms.FileField):
            continue  # a file input left empty keeps the file
        put(data, form.add_prefix(name), form[name].value())


def put_values(data, form, values, label="fields"):
    allowed = form_field_names(type(form))
    unknown = sorted(set(values) - set(allowed))
    if unknown:
        raise InvalidArguments(
            f"{label}: unknown {', '.join(unknown)}; valid: {', '.join(allowed)}."
        )
    notes = []
    for name, value in values.items():
        field = form.fields[name]
        if isinstance(field, forms.FileField):
            raise ToolError(f"{label}.{name}: files cannot be set over MCP yet.")
        if isinstance(field.widget, CkEditorWidgetBase) and isinstance(value, str):
            value, cleaned = clean_html(value, text_rules(field.widget))
            notes += [f"{label}.{name}: {note}" for note in cleaned]
        put(data, form.add_prefix(name), value)
    return notes


def put(data, key, value):
    if isinstance(value, (list, tuple)):
        data.setlist(key, [encode(item) for item in value])
    else:
        data[key] = encode(value)


def encode(value):
    if value is None:
        return ""
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, models.Model):
        return str(value.pk)
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def invalid(form):
    """``form_error`` for ``form`` and its configs' forms together."""
    errors = form_error(form).data["fields"]
    for config in form.xprez_configs:
        if config.admin_form.errors:
            for name, messages in form_error(config.admin_form).data["fields"].items():
                errors[f"configs.{config.css_breakpoint}.{name}"] = messages
    summary = "; ".join(
        f"{name}: {' '.join(messages)}" for name, messages in errors.items()
    )
    return ToolError(f"Invalid data. {summary}", data={"fields": errors})


def reorder(siblings, obj=None, index=None):
    """Put ``obj`` at ``index`` among ``siblings`` (``None``: last) and number
    them 0, 1, ... in that order; without ``obj``, only number them. Rows are
    updated directly; the caller invalidates the front cache."""
    siblings = sorted(siblings, key=lambda sibling: (sibling.position, sibling.pk))
    if obj is not None:
        siblings = [
            sibling for sibling in siblings if identity(sibling) != identity(obj)
        ]
        if index is None or index > len(siblings):
            index = len(siblings)
        siblings.insert(max(index, 0), obj)
    for position, sibling in enumerate(siblings):
        if sibling.position != position:
            type(sibling).objects.filter(pk=sibling.pk).update(position=position)
            sibling.position = position


def identity(obj):
    """``(root model, pk)``: a base ``Module`` row and its concrete module are
    the same object."""
    parents = obj._meta.get_parent_list()
    return (parents[-1] if parents else type(obj), obj.pk)
