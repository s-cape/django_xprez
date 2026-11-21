"""``XprezProvider``: xprez content as MCP tools.

By default it follows the admin: every container model registered on the
admin site with an ``XprezAdmin`` is exposed, and a user sees and changes
through MCP what they see and change on that container's change page.

Projects with other rules subclass it and override the hooks under
"containers and permissions" (``get_container_models``,
``get_container_queryset``, ``has_container_permission``,
``search_containers``, ``log_change``). Writes always go through an
``XprezAdminMixin``, which needs no ``ModelAdmin``.
"""

from typing import Annotated, Any, Literal, Optional

from django.apps import apps
from django.contrib import admin
from django.db import transaction
from django.db.models import Q

from xprez_mcp import InvalidArguments, Provider, ToolError, resource, tool
from xprez_mcp.core.items import Item
from xprez_mcp.providers.admin.request import get_admin_request

from xprez import models as xprez_models
from xprez.admin.admin import XprezAdminMixin
from xprez.admin.forms import SectionForm
from xprez.conf import settings
from xprez.models.multi_module import MultiModule
from xprez.modules.symlink import ModuleSymlink

from . import guide
from .forms import reorder, write_module, write_section
from .serialize import form_field_names, form_schema, model_values

GuideTopic = Literal[tuple(guide.TOPICS)]
SectionKind = Literal["section", "section_symlink", "container_symlink"]
Values = Annotated[
    Optional[dict[str, Any]], "Field values to set; xprez_module_types lists them"
]
Configs = Annotated[
    Optional[dict[str, Optional[dict[str, Any]]]],
    'Config values per breakpoint, like {"0": {...}, "5": {...}}; '
    "null removes a breakpoint's config",
]

SECTION_KINDS = {
    "section": xprez_models.Section,
    "section_symlink": xprez_models.SectionSymlink,
    "container_symlink": xprez_models.ContainerSymlink,
}


class NotFound(ToolError):
    """An object that does not exist, or that the user may not see."""


class XprezItem(Item):
    """Write tools need the change permission on some container model."""

    def is_allowed(self, ctx):
        if not super().is_allowed(ctx):
            return False
        if self.kind != "tool" or self.spec.hints.get("readOnlyHint"):
            return True
        return self.provider.can_write(ctx)


class XprezProvider(Provider):
    namespace = "xprez"
    admin_site = None  # default: django.contrib.admin.site
    page_size = 20
    max_page_size = 100

    # --- containers and permissions: the hooks --------------------------------

    def get_container_models(self, ctx):
        """``{model: xprez_admin}`` of the container models ``ctx``'s user may
        use. ``xprez_admin`` is an ``XprezAdminMixin`` with ``model`` set (a
        ``ModelAdmin`` or not): it builds the forms and decides the allowed
        modules.

        Default: the ``XprezAdmin``s on the admin site the user may view.
        """
        request = self.admin_request(ctx)
        if not self.get_admin_site().has_permission(request):
            return {}
        return {
            model: xprez_admin
            for model, xprez_admin in self.get_admin_site()._registry.items()
            if issubclass(model, xprez_models.Container)
            and isinstance(xprez_admin, XprezAdminMixin)
            and getattr(model, "mcp_exposed", True)
            and getattr(xprez_admin, "mcp_exposed", True)
            and xprez_admin.has_module_permission(request)
        }

    def get_container_queryset(self, ctx, model, xprez_admin, write=False):
        """The containers of ``model`` that exist for ``ctx``'s user.

        Default: the admin's ``get_queryset``, narrowed by
        ``xprez_get_container_qs`` (only the latter without a ``ModelAdmin``).
        """
        request = self.admin_request(ctx, write=write)
        allowed = xprez_admin.xprez_get_container_qs(request).values("pk")
        if isinstance(xprez_admin, admin.ModelAdmin):
            queryset = xprez_admin.get_queryset(request)
        else:
            queryset = model._default_manager.all()
        return queryset.filter(pk__in=allowed)

    def has_container_permission(
        self, ctx, model, xprez_admin, container=None, write=False
    ):
        """Whether ``ctx``'s user may read (with ``write``: change)
        ``container``, or with ``container=None`` some container of ``model``.

        Default: the ``ModelAdmin``'s view/change permissions. Without a
        ``ModelAdmin`` nothing is allowed until this is overridden.
        """
        if not isinstance(xprez_admin, admin.ModelAdmin):
            return False
        request = self.admin_request(ctx, write=write)
        if write:
            return xprez_admin.has_change_permission(request, container)
        return xprez_admin.has_view_or_change_permission(request, container)

    def search_containers(self, ctx, model, xprez_admin, queryset, query):
        """``queryset`` narrowed by ``query``, or ``None`` when ``model`` cannot
        be searched. Default: the ``ModelAdmin``'s search."""
        if not isinstance(xprez_admin, admin.ModelAdmin):
            return None
        request = self.admin_request(ctx)
        if not xprez_admin.get_search_fields(request):
            return None
        queryset, duplicates = xprez_admin.get_search_results(request, queryset, query)
        return queryset.distinct() if duplicates else queryset

    def log_change(self, ctx, model, xprez_admin, container, message):
        """Record a change. Default: the ``ModelAdmin``'s history, if any."""
        if isinstance(xprez_admin, admin.ModelAdmin):
            request = self.admin_request(ctx, write=True)
            xprez_admin.log_change(request, container, f"{message} (MCP)")

    # --- containers and permissions: built on the hooks -----------------------

    def get_admin_site(self):
        return self.admin_site or admin.site

    def admin_request(self, ctx, write=False):
        """The request admin and form code gets (``xprez_get_container_qs``,
        ``save_admin_form``), one per call."""
        return get_admin_request(ctx, self.get_admin_site(), write=write)

    def visible_models(self, ctx):
        """``get_container_models`` limited to the models the user may read."""
        return {
            model: xprez_admin
            for model, xprez_admin in self.get_container_models(ctx).items()
            if self.has_container_permission(ctx, model, xprez_admin)
        }

    def has_permission(self, ctx):
        return bool(self.visible_models(ctx))

    def can_write(self, ctx):
        return any(
            self.has_container_permission(ctx, model, xprez_admin, write=True)
            for model, xprez_admin in self.visible_models(ctx).items()
        )

    def get_items(self):
        return [XprezItem(spec, self) for spec in self.get_specs()]

    def get_container(self, ctx, container_id, write=False):
        """``(container, xprez_admin)``, or a ``ToolError`` as if it did not exist."""
        not_found = NotFound(f"Container {container_id} does not exist.")
        base = (
            xprez_models.Container.objects.filter(pk=container_id)
            .only("content_type")
            .first()
        )
        if base is None:
            raise not_found
        model = apps.get_model(base.content_type)
        xprez_admin = self.visible_models(ctx).get(model)
        if xprez_admin is None:
            raise not_found
        container = (
            self.get_container_queryset(ctx, model, xprez_admin, write=write)
            .filter(pk=container_id)
            .first()
        )
        if container is None:
            raise not_found
        if not self.has_container_permission(
            ctx, model, xprez_admin, container, write=write
        ):
            if write:
                raise ToolError(f"You cannot change container {container_id}.")
            raise not_found
        return container, xprez_admin

    def get_module(self, ctx, module_id, write=False):
        """The concrete module; with ``write``, ``(module, container, admin)``."""
        module = (
            xprez_models.Module.objects.filter(pk=module_id)
            .select_related("section")
            .first()
        )
        if module is None:
            raise NotFound(f"Module {module_id} does not exist.")
        try:
            container, xprez_admin = self.get_container(
                ctx, module.section.container_id, write=write
            )
        except NotFound:
            raise NotFound(f"Module {module_id} does not exist.") from None
        if write:
            return module.polymorph, container, xprez_admin
        return module.polymorph

    def get_section(self, ctx, section_id, kind="section"):
        """``(section, container, admin)`` for a write."""
        section = SECTION_KINDS[kind].objects.filter(pk=section_id).first()
        if section is None:
            raise NotFound(f"{kind} {section_id} does not exist.")
        try:
            container, xprez_admin = self.get_container(
                ctx, section.container_id, write=True
            )
        except NotFound:
            raise NotFound(f"{kind} {section_id} does not exist.") from None
        return section, container, xprez_admin

    def module_classes(self, xprez_admin, container):
        """``{type: class}`` of the modules the admin's add menu offers."""
        return {
            module_class.module_key: module_class
            for module_class in xprez_admin.xprez_add_menu_module_classes(container)
        }

    def log(self, ctx, xprez_admin, container, message):
        """Record a change and refresh the container's front cache."""
        self.log_change(ctx, container.__class__, xprez_admin, container, message)
        container.invalidate_front_cache()

    # --- read tools ---------------------------------------------------------

    @tool(read_only=True)
    def guide(self, ctx, topic: GuideTopic = "index"):
        """How xprez content is structured and how to edit it well. Read the
        index before your first change; it lists the other topics."""
        return guide.render_topic(topic)

    @tool(read_only=True)
    def containers_list(
        self,
        ctx,
        type: Annotated[
            Optional[str], "Container type, like example_app.page; default all"
        ] = None,
        query: Annotated[Optional[str], "Search, as in the admin's list"] = None,
        limit: int = 20,
        cursor: Optional[str] = None,
    ):
        """Find pages and other containers with xprez content."""
        models = self.visible_models(ctx)
        types = {container_type(model): model for model in models}
        if type is not None:
            if type not in types:
                raise InvalidArguments(f"type must be one of {sorted(types)}.")
            models = {types[type]: models[types[type]]}
        condition = Q(pk__in=[])
        for model, xprez_admin in models.items():
            queryset = self.get_container_queryset(ctx, model, xprez_admin)
            if query:
                queryset = self.search_containers(
                    ctx, model, xprez_admin, queryset, query
                )
                if queryset is None:
                    if type is not None:
                        raise InvalidArguments(f"{type} cannot be searched.")
                    continue
            condition |= Q(pk__in=queryset.values("pk"))
        queryset = xprez_models.Container.objects.filter(condition).order_by("-pk")
        offset = decode_cursor(cursor)
        limit = max(1, min(limit, self.max_page_size))
        rows = list(queryset[offset : offset + limit])
        count = queryset.count()
        return {
            "results": [
                self.container_summary(container, models[container.__class__])
                for container in polymorphs(rows)
            ],
            "count": count,
            "next_cursor": (str(offset + limit) if offset + limit < count else None),
        }

    @tool(read_only=True)
    def container_get(self, ctx, container: int):
        """The content of a container: its sections and their modules, in
        order. Configs show only the values that differ from the defaults;
        xprez_module_get returns a module in full."""
        obj, xprez_admin = self.get_container(ctx, container)
        return {
            **self.container_summary(obj, xprez_admin),
            "breakpoints": breakpoints(),
            "linked_from": sorted(
                set(
                    xprez_models.ContainerSymlink.objects.filter(
                        symlink=obj, saved=True
                    ).values_list("container_id", flat=True)
                )
            ),
            "sections": [
                self.serialize_section_item(item)
                for item in obj._get_ordered_section_items()
                if item.saved
            ],
        }

    @tool(read_only=True)
    def module_get(self, ctx, module: int):
        """One module in full: its fields, its configs per breakpoint and, for
        modules with items, the items."""
        obj = self.get_module(ctx, module)
        result = {
            "id": obj.pk,
            "type": obj.module_key,
            "section": obj.section_id,
            "container": obj.section.container_id,
            "position": obj.position,
            "fields": model_values(obj, form_field_names(obj.get_admin_form_class())),
            "configs": serialize_configs(obj, compact=False),
        }
        if isinstance(obj, ModuleSymlink):
            result["links_to"] = {"module": obj.symlink_id}
        if isinstance(obj, MultiModule):
            result["items"] = serialize_items(obj)
        return result

    @tool(read_only=True)
    def module_types(
        self,
        ctx,
        container: int,
        type: Annotated[
            Optional[str], "A module type, for its fields; default: list all"
        ] = None,
    ):
        """The module types this container allows. With `type`, the fields
        that type, its configs and its items take."""
        obj, xprez_admin = self.get_container(ctx, container)
        classes = self.module_classes(xprez_admin, obj)
        if type is None:
            return {
                "types": [
                    {
                        "type": key,
                        "name": str(module_class._meta.verbose_name),
                        "summary": guide.module_summary(module_class),
                        "has_items": issubclass(module_class, MultiModule),
                    }
                    for key, module_class in classes.items()
                ]
            }
        if type not in classes:
            raise InvalidArguments(f"type must be one of {sorted(classes)}.")
        return module_type_schema(classes[type])

    # --- write tools --------------------------------------------------------

    @tool
    @transaction.atomic
    def section_add(
        self,
        ctx,
        container: int,
        position: Annotated[
            Optional[int], "Index among the sections; default last"
        ] = None,
        fields: Values = None,
        configs: Configs = None,
    ):
        """Add an empty section to a container. Changes are live at once.
        Read xprez_guide (index, editing) before your first change."""
        obj, xprez_admin = self.get_container(ctx, container, write=True)
        section = xprez_admin._xprez_create_section(obj)
        self.save_section(ctx, xprez_admin, section, fields, configs)
        reorder(obj._get_ordered_section_items(), section, position)
        self.log(ctx, xprez_admin, obj, f"Added section {section.pk}")
        return self.section_result(section)

    @tool(idempotent=True)
    @transaction.atomic
    def section_update(
        self, ctx, section: int, fields: Values = None, configs: Configs = None
    ):
        """Change a section's fields and configs; leave out what stays. Changes
        are live at once and show on every page linking to the section.
        Read xprez_guide (index, editing) before your first change."""
        obj, container, xprez_admin = self.get_section(ctx, section)
        self.save_section(ctx, xprez_admin, obj, fields, configs)
        self.log(ctx, xprez_admin, container, f"Changed section {obj.pk}")
        return self.section_result(obj)

    @tool(idempotent=True)
    @transaction.atomic
    def section_move(
        self,
        ctx,
        section: int,
        position: Annotated[int, "Index among the container's sections, from 0"],
        kind: SectionKind = "section",
    ):
        """Move a section, or a link to a section or container, to another
        position in its container."""
        obj, container, xprez_admin = self.get_section(ctx, section, kind)
        reorder(container._get_ordered_section_items(), obj, position)
        self.log(ctx, xprez_admin, container, f"Moved {kind} {obj.pk}")
        return self.container_get(ctx, container.pk)

    @tool(destructive=True)
    @transaction.atomic
    def section_delete(self, ctx, section: int, kind: SectionKind = "section"):
        """Delete a section with all its modules, or a link. Live at once and
        cannot be undone; on other pages, links to the section show nothing."""
        obj, container, xprez_admin = self.get_section(ctx, section, kind)
        obj.delete()
        reorder(container._get_ordered_section_items())
        self.log(ctx, xprez_admin, container, f"Deleted {kind} {section}")
        return {"deleted": True, "kind": kind, "id": section}

    @tool
    @transaction.atomic
    def module_add(
        self,
        ctx,
        type: Annotated[str, "Module type, from xprez_module_types"],
        section: Annotated[Optional[int], "Add to this section"] = None,
        container: Annotated[
            Optional[int], "Or add a new section with the module to this container"
        ] = None,
        position: Annotated[
            Optional[int], "Index in the section (or of the new section); default last"
        ] = None,
        fields: Values = None,
        configs: Configs = None,
    ):
        """Add a module to a section, or a new section with the module to a
        container. Changes are live at once.
        Read xprez_guide (index, editing) before your first change."""
        if (section is None) == (container is None):
            raise InvalidArguments("Give either section or container.")
        if section is not None:
            target, obj, xprez_admin = self.get_section(ctx, section)
        else:
            obj, xprez_admin = self.get_container(ctx, container, write=True)
        module_class = self.module_classes(xprez_admin, obj).get(type)
        if module_class is None:
            raise InvalidArguments(
                f"type must be one of {sorted(self.module_classes(xprez_admin, obj))}."
            )
        request = self.admin_request(ctx, write=True)
        if section is None:
            content_type = module_class.class_content_type()
            target = xprez_admin._xprez_create_section(obj, content_type)
            write_section(xprez_admin, request, target, {}, {})
            reorder(obj._get_ordered_section_items(), target, position)
            position = None
        module = xprez_admin._xprez_create_module(module_class, target)
        self.save_module(ctx, xprez_admin, module, fields, configs)
        reorder(target.modules.all(), module, position)
        self.log(
            ctx,
            xprez_admin,
            obj,
            f"Added {module_class._meta.verbose_name} {module.pk}",
        )
        return self.module_get(ctx, module.pk)

    @tool(idempotent=True)
    @transaction.atomic
    def module_update(
        self, ctx, module: int, fields: Values = None, configs: Configs = None
    ):
        """Change a module's fields and configs; leave out what stays. Changes
        are live at once and show wherever the module is linked.
        Read xprez_guide (index, editing) before your first change."""
        obj, container, xprez_admin = self.get_module(ctx, module, write=True)
        self.save_module(ctx, xprez_admin, obj, fields, configs)
        self.log(
            ctx, xprez_admin, container, f"Changed {obj._meta.verbose_name} {obj.pk}"
        )
        return self.module_get(ctx, obj.pk)

    @tool(idempotent=True)
    @transaction.atomic
    def module_move(
        self,
        ctx,
        module: int,
        position: Annotated[
            Optional[int], "Index in the section, from 0; default last"
        ] = None,
        section: Annotated[
            Optional[int], "Move to this section of the same container"
        ] = None,
    ):
        """Move a module within its section or to another section of the same
        container."""
        obj, container, xprez_admin = self.get_module(ctx, module, write=True)
        source = obj.section
        if section is not None and section != source.pk:
            target, target_container, _xprez_admin = self.get_section(ctx, section)
            if target_container.pk != container.pk:
                raise InvalidArguments("section must be in the module's container.")
            xprez_models.Module.objects.filter(pk=obj.pk).update(section=target)
            obj.section = target
            reorder(source.modules.all())
            source.invalidate_front_cache()
        reorder(obj.section.modules.all(), obj, position)
        obj.invalidate_front_cache()
        self.log(
            ctx, xprez_admin, container, f"Moved {obj._meta.verbose_name} {obj.pk}"
        )
        return self.module_get(ctx, obj.pk)

    @tool(destructive=True)
    @transaction.atomic
    def module_delete(self, ctx, module: int):
        """Delete a module. Live at once and cannot be undone; links to the
        module on other pages show nothing."""
        obj, container, xprez_admin = self.get_module(ctx, module, write=True)
        name = obj._meta.verbose_name
        section = obj.section
        obj.delete()
        reorder(section.modules.all())
        self.log(ctx, xprez_admin, container, f"Deleted {name} {module}")
        return {"deleted": True, "id": module}

    def save_section(self, ctx, xprez_admin, section, fields, configs):
        request = self.admin_request(ctx, write=True)
        write_section(
            xprez_admin, request, section, fields or {}, parse_configs(configs)
        )

    def save_module(self, ctx, xprez_admin, module, fields, configs):
        request = self.admin_request(ctx, write=True)
        write_module(xprez_admin, request, module, fields or {}, parse_configs(configs))

    def section_result(self, section):
        section.refresh_from_db()
        return {
            "kind": "section",
            "id": section.pk,
            "container": section.container_id,
            "position": section.position,
            "fields": model_values(section, form_field_names(SectionForm)),
            "configs": serialize_configs(section, compact=False),
        }

    # --- resources ----------------------------------------------------------

    @resource("xprez://guide", mime_type="text/markdown")
    def guide_index(self, ctx):
        """The xprez editing guide: start here."""
        return guide.render_topic("index")

    @resource("xprez://guide/{topic}", mime_type="text/markdown")
    def guide_topic(self, ctx, topic: GuideTopic):
        """One topic of the xprez editing guide."""
        return guide.render_topic(topic)

    @guide_topic.complete("topic")
    def _guide_topics(self, ctx, value):
        return [topic for topic in guide.TOPICS if topic.startswith(value)]

    @resource("xprez://containers/{id}", mime_type="text/html")
    def container_html(self, ctx, id: int):
        """A container's content rendered as on the site, to check changes."""
        obj, _xprez_admin = self.get_container(ctx, id)
        return obj.render_front({"request": self.admin_request(ctx)})

    # --- serialization ------------------------------------------------------

    def container_summary(self, container, xprez_admin):
        result = {
            "id": container.pk,
            "type": container_type(container.__class__),
            "display": str(container),
            "admin_url": xprez_admin.xprez_admin_change_url(container),
        }
        get_url = getattr(container, "get_absolute_url", None)
        if get_url is not None:
            result["url"] = get_url()
        return result

    def serialize_section_item(self, item):
        if isinstance(item, xprez_models.SectionSymlink):
            return {
                "kind": "section_symlink",
                "id": item.pk,
                "position": item.position,
                "visible": item.visible,
                "links_to": {
                    "section": item.symlink_id,
                    "container": item.symlink.container_id if item.symlink else None,
                },
            }
        if isinstance(item, xprez_models.ContainerSymlink):
            return {
                "kind": "container_symlink",
                "id": item.pk,
                "position": item.position,
                "visible": item.visible,
                "links_to": {"container": item.symlink_id},
            }
        return {
            "kind": "section",
            "id": item.pk,
            "position": item.position,
            "fields": model_values(item, form_field_names(SectionForm)),
            "configs": serialize_configs(item, compact=True),
            "linked_from": sorted(
                set(
                    xprez_models.SectionSymlink.objects.filter(
                        symlink=item, saved=True
                    ).values_list("container_id", flat=True)
                )
            ),
            "modules": [
                self.serialize_module_summary(module)
                for module in item.modules.filter(saved=True).polymorphs()
            ],
        }

    def serialize_module_summary(self, module):
        result = {
            "id": module.pk,
            "type": module.module_key,
            "position": module.position,
            "preview": module.preview_text(),
            "configs": serialize_configs(module, compact=True),
        }
        if isinstance(module, ModuleSymlink):
            result["links_to"] = {"module": module.symlink_id}
        else:
            linked = ModuleSymlink.objects.filter(
                symlink=module, saved=True
            ).values_list("section__container_id", flat=True)
            result["linked_from"] = sorted(set(linked))
        return result


def container_type(model):
    return f"{model._meta.app_label}.{model._meta.model_name}"


def polymorphs(containers):
    """The concrete containers of ``containers``, one query per type, in order."""
    by_type = {}
    for container in containers:
        by_type.setdefault(container.content_type, []).append(container.pk)
    found = {}
    for content_type, pks in by_type.items():
        for obj in apps.get_model(content_type).objects.filter(pk__in=pks):
            found[obj.pk] = obj
    return [found[container.pk] for container in containers if container.pk in found]


def breakpoints():
    return {
        str(number): guide.breakpoint_name(number)
        for number in settings.XPREZ_BREAKPOINTS
    }


def serialize_configs(parent, compact):
    """``{breakpoint: values}``; ``compact`` leaves out values a new config
    would have (``XPREZ_DEFAULTS``)."""
    result = {}
    for config in parent.get_configs().filter(saved=True):
        names = form_field_names(config.get_admin_form_class())
        values = model_values(config, names)
        if compact:
            defaults = model_values(parent.build_config(config.css_breakpoint), names)
            values = {
                name: value
                for name, value in values.items()
                if value != defaults.get(name)
            }
        result[str(config.css_breakpoint)] = values
    return result


def serialize_items(module):
    items = list(
        getattr(module, module.items_attribute)
        .filter(saved=True)
        .order_by("position", "pk")
    )
    if not items:
        return []
    names = form_field_names(module.get_admin_item_form_class(items[0]))
    return [
        {"id": item.pk, "position": item.position, **model_values(item, names)}
        for item in items
    ]


def module_type_schema(module_class):
    module = module_class()
    config = module.get_config_model()(css_breakpoint=0)
    result = {
        "type": module_class.module_key,
        "name": str(module_class._meta.verbose_name),
        "summary": guide.module_summary(module_class),
        "fields": form_schema(module.get_admin_form_class()),
        "config_fields": form_schema(config.get_admin_form_class()),
    }
    if issubclass(module_class, MultiModule):
        item = module.build_item()
        result["item_fields"] = form_schema(module.get_admin_item_form_class(item))
    return result


def parse_configs(configs):
    """``{breakpoint number: values or None}`` from the JSON object."""
    result = {}
    for key, values in (configs or {}).items():
        try:
            result[int(key)] = values
        except ValueError:
            raise InvalidArguments(
                f"configs: {key!r} is not a breakpoint number."
            ) from None
    return result


def decode_cursor(cursor):
    if cursor is None:
        return 0
    try:
        offset = int(cursor)
    except ValueError:
        raise InvalidArguments("cursor is invalid.") from None
    if offset < 0:
        raise InvalidArguments("cursor is invalid.")
    return offset
