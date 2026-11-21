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

from xprez.conf import settings
from xprez.utils import import_class

from .serialize import form_field_names

SECTION_FORM = "xprez.admin.forms.SectionForm"


def write_module(model_admin, request, module, fields, configs):
    """Validate and save ``fields`` and ``configs`` on ``module``."""
    prepare_configs(module, configs)
    module.build_admin_form(model_admin)
    data = QueryDict(mutable=True)
    put_form(data, module.admin_form)
    put_values(data, module.admin_form, fields)
    put_configs(data, "module-config-id", module.admin_form.xprez_configs, configs)
    if hasattr(module, "items_attribute"):  # items have their own tools
        data.setlist(f"{module.instance_key}-item-id", [])
    module.build_admin_form(model_admin, data=data, files=MultiValueDict())
    if not module.is_admin_form_valid():
        raise invalid(module.admin_form, module.admin_form.xprez_configs)
    module.save_admin_form(request)


def write_section(model_admin, request, section, fields, configs):
    """Validate and save ``fields`` and ``configs`` on ``section``; its modules
    are left as they are (``Section.save_admin_form`` would save them too)."""
    prepare_configs(section, configs)
    form_class = import_class(SECTION_FORM)
    unbound = form_class(instance=section, prefix=section.instance_key)
    section_configs = list(section.get_configs())
    for config in section_configs:
        config.build_admin_form(model_admin)
    data = QueryDict(mutable=True)
    put_form(data, unbound)
    put_values(data, unbound, fields)
    put_configs(data, "section-config-id", section_configs, configs)

    form = form_class(instance=section, prefix=section.instance_key, data=data)
    for config in section_configs:
        config.build_admin_form(model_admin, data, MultiValueDict())
    valid = form.is_valid()
    valid = all([config.is_admin_form_valid() for config in section_configs]) and valid
    if not valid:
        raise invalid(form, section_configs)
    instance = form.save(commit=False)
    instance.saved = True
    instance.save()
    for config in section_configs:
        config.save_admin_form(request)
    section._prune_redundant_configs()


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
    for config in parent_configs:
        form = config.admin_form
        put_form(data, form)
        values = configs.get(config.css_breakpoint, {})
        if values is None:
            data[form.add_prefix("delete")] = "on"
        else:
            put_values(data, form, values, label=f"configs.{config.css_breakpoint}")


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
    for name, value in values.items():
        if isinstance(form.fields[name], forms.FileField):
            raise ToolError(f"{label}.{name}: files cannot be set over MCP yet.")
        put(data, form.add_prefix(name), value)


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


def invalid(form, configs):
    """A ``ToolError`` with the errors of ``form`` and its configs' forms."""
    errors = {}
    for name, messages in form.errors.items():
        errors[name] = list(messages)
    for config in configs:
        for name, messages in config.admin_form.errors.items():
            errors[f"configs.{config.css_breakpoint}.{name}"] = list(messages)
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
