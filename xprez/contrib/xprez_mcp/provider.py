"""``XprezProvider``: xprez content as MCP tools, with the admin's permissions.

Every container model registered on the admin site with an ``XprezAdmin`` is
exposed. A user sees and changes through MCP what they see and change on that
container's admin change page: the container admin's ``get_queryset`` and
``xprez_get_container_qs`` decide which containers exist for them, its
view/change permissions which tools they get.
"""

from typing import Annotated, Literal, Optional

from django.apps import apps
from django.contrib import admin
from django.db.models import Q

from xprez_mcp import InvalidArguments, Provider, ToolError, resource, tool
from xprez_mcp.providers.admin.request import get_admin_request

from xprez import models as xprez_models
from xprez.admin.admin import XprezAdminMixin
from xprez.admin.forms import SectionForm
from xprez.conf import settings
from xprez.models.multi_module import MultiModule
from xprez.modules.symlink import ModuleSymlink

from . import guide
from .serialize import form_field_names, form_schema, model_values

GuideTopic = Literal[tuple(guide.TOPICS)]


class XprezProvider(Provider):
    namespace = "xprez"
    admin_site = None  # default: django.contrib.admin.site
    page_size = 20
    max_page_size = 100

    # --- containers and permissions -----------------------------------------

    def get_admin_site(self):
        return self.admin_site or admin.site

    def container_admins(self):
        """``{model: model_admin}`` of the containers on the admin site."""
        return {
            model: model_admin
            for model, model_admin in self.get_admin_site()._registry.items()
            if issubclass(model, xprez_models.Container)
            and isinstance(model_admin, XprezAdminMixin)
            and getattr(model, "mcp_exposed", True)
            and getattr(model_admin, "mcp_exposed", True)
        }

    def admin_request(self, ctx, write=False):
        return get_admin_request(ctx, self.get_admin_site(), write=write)

    def visible_admins(self, ctx):
        request = self.admin_request(ctx)
        return {
            model: model_admin
            for model, model_admin in self.container_admins().items()
            if model_admin.has_module_permission(request)
            and model_admin.has_view_or_change_permission(request)
        }

    def has_permission(self, ctx):
        request = self.admin_request(ctx)
        return self.get_admin_site().has_permission(request) and bool(
            self.visible_admins(ctx)
        )

    def container_queryset(self, ctx, model_admin, write=False):
        request = self.admin_request(ctx, write=write)
        allowed = model_admin.xprez_get_container_qs(request).values("pk")
        return model_admin.get_queryset(request).filter(pk__in=allowed)

    def get_container(self, ctx, container_id, write=False):
        """``(container, model_admin)``, or a ``ToolError`` as if it did not exist."""
        not_found = ToolError(f"Container {container_id} does not exist.")
        base = (
            xprez_models.Container.objects.filter(pk=container_id)
            .only("content_type")
            .first()
        )
        if base is None:
            raise not_found
        model_admin = self.visible_admins(ctx).get(apps.get_model(base.content_type))
        if model_admin is None:
            raise not_found
        container = (
            self.container_queryset(ctx, model_admin, write=write)
            .filter(pk=container_id)
            .first()
        )
        if container is None:
            raise not_found
        request = self.admin_request(ctx, write=write)
        if write:
            allowed = model_admin.has_change_permission(request, container)
        else:
            allowed = model_admin.has_view_or_change_permission(request, container)
        if not allowed:
            raise ToolError(f"You cannot change container {container_id}.")
        return container, model_admin

    def get_module(self, ctx, module_id, write=False):
        module = (
            xprez_models.Module.objects.filter(pk=module_id)
            .select_related("section")
            .first()
        )
        if module is None:
            raise ToolError(f"Module {module_id} does not exist.")
        try:
            self.get_container(ctx, module.section.container_id, write=write)
        except ToolError:
            raise ToolError(f"Module {module_id} does not exist.") from None
        return module.polymorph

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
        admins = self.visible_admins(ctx)
        types = {container_type(model): model for model in admins}
        if type is not None:
            if type not in types:
                raise InvalidArguments(f"type must be one of {sorted(types)}.")
            admins = {types[type]: admins[types[type]]}
        request = self.admin_request(ctx)
        condition = Q(pk__in=[])
        for model, model_admin in admins.items():
            queryset = self.container_queryset(ctx, model_admin)
            if query:
                if not model_admin.get_search_fields(request):
                    if type is not None:
                        raise InvalidArguments(f"{type} cannot be searched.")
                    continue
                queryset, _duplicates = model_admin.get_search_results(
                    request, queryset, query
                )
            condition |= Q(pk__in=queryset.values("pk"))
        queryset = xprez_models.Container.objects.filter(condition).order_by("-pk")
        offset = decode_cursor(cursor)
        limit = max(1, min(limit, self.max_page_size))
        rows = list(queryset[offset : offset + limit])
        count = queryset.count()
        return {
            "results": [
                self.container_summary(ctx, container) for container in polymorphs(rows)
            ],
            "count": count,
            "next_cursor": (str(offset + limit) if offset + limit < count else None),
        }

    @tool(read_only=True)
    def container_get(self, ctx, container: int):
        """The content of a container: its sections and their modules, in
        order. Configs show only the values that differ from the defaults;
        xprez_module_get returns a module in full."""
        obj, _model_admin = self.get_container(ctx, container)
        return {
            **self.container_summary(ctx, obj),
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
        obj, model_admin = self.get_container(ctx, container)
        classes = {
            module_class.module_key: module_class
            for module_class in model_admin.xprez_add_menu_module_classes(obj)
        }
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
        obj, _model_admin = self.get_container(ctx, id)
        return obj.render_front({"request": self.admin_request(ctx)})

    # --- serialization ------------------------------------------------------

    def container_summary(self, ctx, container):
        model_admin = self.container_admins()[type(container)]
        result = {
            "id": container.pk,
            "type": container_type(type(container)),
            "display": str(container),
            "admin_url": model_admin.xprez_admin_change_url(container),
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
