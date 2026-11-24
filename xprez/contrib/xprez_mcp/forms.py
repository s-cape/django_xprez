"""Writes through the admin's forms.

Each write builds the data the admin change page would post for the object:
the current value of every field, with the values sent over MCP on top (a
``ModelForm`` reads a missing field as empty). The objects' own
``build_admin_form`` / ``is_admin_form_valid`` / ``save_admin_form`` then
validate and save it, so the admin's rules hold over MCP too. Files sent
for file fields go in the form's ``files``, resolved by the provider's
``FileArgumentsMixin``.
"""

from django import forms
from django.db import models
from django.http import QueryDict
from xprez_mcp import InvalidArguments, ToolError
from xprez_mcp.providers.files import closing_stored_files, form_files
from xprez_mcp.providers.model import form_error

from xprez.ck_editor.widgets import CkEditorWidgetBase
from xprez.conf import settings

from .html import clean_html, text_rules
from .serialize import form_field_names


def write(provider, ctx, xprez_admin, obj, fields, configs, items=None):
    """Validate and save ``fields`` and ``configs`` on a section or module
    through its own admin form; returns notes on what was changed in the
    values sent (cleaned HTML).

    ``items`` (``{item: values, or None to delete it}``) writes items of a
    module with items; the module's other items, like a section's modules,
    are left out of the form and stay as they are."""
    items = {item.pk: values for item, values in (items or {}).items()}
    prepare_configs(obj, configs)
    obj.build_admin_form(xprez_admin)
    form = obj.admin_form
    post = Post(provider, ctx)
    put_form(post.data, form)
    notes = put_values(post, form, fields)
    notes += put_configs(post, f"{obj.KEY}-config-id", form.xprez_configs, configs)
    if hasattr(obj, "items_attribute"):
        post.data.setlist(f"{obj.instance_key}-item-id", [str(pk) for pk in items])
        for item in form.xprez_items:
            if item.pk in items:
                notes += put_item(post, item, items[item.pk])
    obj.build_admin_form(xprez_admin, data=post.data, files=form_files(post.files))
    if hasattr(obj.admin_form, "xprez_modules"):
        obj.admin_form.xprez_modules = []
    with closing_stored_files(post.files):
        valid = obj.is_admin_form_valid()
    if not valid:
        raise invalid(obj.admin_form)
    with provider.removing_uploads_on_error(post.files.values()):
        obj.save_admin_form(provider.admin_request(ctx, write=True))
    return notes


class Post:
    """What the admin page would post: ``data``, and ``files`` from the file
    arguments (``False`` clears a file)."""

    def __init__(self, provider, ctx):
        self.provider, self.ctx = provider, ctx
        self.data = QueryDict(mutable=True)
        self.files = {}

    def put_file(self, form, name, value, label):
        field = form._meta.model._meta.get_field(name)
        value = self.provider.file_value(value, field, label)
        self.files[form.add_prefix(name)] = (
            False
            if value is None
            else self.provider.resolve_file(self.ctx, field, value)
        )


def put_item(post, item, values):
    put_form(post.data, item.admin_form)
    if values is None:
        post.data[item.admin_form.add_prefix("delete")] = "on"
        return []
    return put_values(post, item.admin_form, values, label=f"items.{item.pk}")


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


def put_configs(post, id_key, parent_configs, configs):
    post.data.setlist(id_key, [str(config.pk) for config in parent_configs])
    notes = []
    for config in parent_configs:
        form = config.admin_form
        put_form(post.data, form)
        values = configs.get(config.css_breakpoint, {})
        if values is None:
            post.data[form.add_prefix("delete")] = "on"
        else:
            label = f"configs.{config.css_breakpoint}"
            notes += put_values(post, form, values, label=label)
    return notes


def put_form(data, form):
    """The current values of ``form``'s fields, as the admin page posts them."""
    for name, field in form.fields.items():
        if name == "delete" or isinstance(field, forms.FileField):
            continue  # a file input left empty keeps the file
        put(data, form.add_prefix(name), form[name].value())


def put_values(post, form, values, label="fields"):
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
            post.put_file(form, name, value, f"{label}.{name}")
            continue
        if isinstance(field.widget, CkEditorWidgetBase) and isinstance(value, str):
            value, cleaned = clean_html(value, text_rules(field.widget))
            notes += [f"{label}.{name}: {note}" for note in cleaned]
        put(post.data, form.add_prefix(name), value)
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
    """``form_error`` for ``form`` and its configs' and items' forms together."""
    errors = form_error(form).data["fields"]
    related = [
        (f"configs.{config.css_breakpoint}", config.admin_form)
        for config in form.xprez_configs
    ] + [
        (f"items.{item.pk}", item.admin_form)
        for item in getattr(form, "xprez_items", ())
    ]
    for label, related_form in related:
        if related_form.errors:
            for name, messages in form_error(related_form).data["fields"].items():
                errors[f"{label}.{name}"] = messages
    summary = "; ".join(
        f"{name}: {' '.join(messages)}" for name, messages in errors.items()
    )
    return ToolError(f"Invalid data. {summary}", data={"fields": errors})


def reorder(siblings, obj=None, index=None):
    """Put ``obj`` at ``index`` among the saved ``siblings`` (``None``: last)
    and number them 0, 1, ... in that order; without ``obj``, only number
    them. Unsaved siblings (added in an admin page not saved yet) do not
    count and go after them. Rows are updated directly; the caller
    invalidates the front cache."""
    siblings = sorted(siblings, key=lambda sibling: (sibling.position, sibling.pk))
    if obj is not None:
        siblings = [
            sibling for sibling in siblings if identity(sibling) != identity(obj)
        ]
    saved = [sibling for sibling in siblings if sibling.saved]
    if obj is not None:
        if index is None or index > len(saved):
            index = len(saved)
        saved.insert(max(index, 0), obj)
    siblings = saved + [sibling for sibling in siblings if not sibling.saved]
    for position, sibling in enumerate(siblings):
        if sibling.position != position:
            type(sibling).objects.filter(pk=sibling.pk).update(position=position)
            sibling.position = position


def identity(obj):
    """``(root model, pk)``: a base ``Module`` row and its concrete module are
    the same object."""
    parents = obj._meta.get_parent_list()
    return (parents[-1] if parents else type(obj), obj.pk)
