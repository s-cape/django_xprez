from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import path, reverse
from django.utils.functional import cached_property

from xprez import constants, models

CLIPBOARD_DUPLICATE_ACTION = "duplicate"
CLIPBOARD_SYMLINK_ACTION = "symlink"


class ClipboardItemBase:
    key = None

    @staticmethod
    def _render(request, xprez_admin, obj):
        obj.build_admin_form(xprez_admin)
        return {"html": obj.render_admin({"request": request})}

    def __init__(self, pk, xprez_admin, target_container, target_section=None):
        self.pk = pk
        self.xprez_admin = xprez_admin
        self.target_container = target_container
        self.target_section = target_section

    @cached_property
    def obj(self):
        return self._get_obj()

    @cached_property
    def allowed_module_classes(self):
        return set(self.xprez_admin.xprez_allowed_module_classes(self.target_container))

    def _get_obj(self):
        raise NotImplementedError

    @property
    def contained_modules(self):
        """List of module instances contained by this item."""
        raise NotImplementedError

    @property
    def contained_module_classes(self):
        """Set of module classes from contained_modules (for availability checks)."""
        out = set()
        for inst in self.contained_modules:
            is_linked = (
                isinstance(inst, models.ModuleSymlink) and inst.symlink_id is not None
            )
            if is_linked:
                out.add(inst.symlink.polymorph.__class__)
            else:
                out.add(inst.__class__)
        return out

    @property
    def allowed(self):
        contained = self.contained_module_classes
        allowed = self.allowed_module_classes
        if contained <= allowed:
            return True
        elif not (contained & allowed):
            return False
        else:
            return "partial"

    def _paste_url(self, action):
        args = [self.key, self.obj.pk, action, self.target_container.pk]
        if self.target_section:
            args += [self.target_section.pk]
        return reverse(self.xprez_admin.xprez_clipboard_paste_url_name(), args=args)

    @property
    def symlink_allowed(self):
        return True

    @property
    def duplicate_url(self):
        return self._paste_url(CLIPBOARD_DUPLICATE_ACTION)

    @property
    def symlink_url(self):
        return self._paste_url(CLIPBOARD_SYMLINK_ACTION)

    @property
    def remove_url(self):
        return reverse(
            self.xprez_admin.xprez_clipboard_remove_url_name(),
            args=[self.key, self.obj.pk],
        )

    def duplicate(self, request, target_section=None):
        raise NotImplementedError

    def symlink(self, request, target_section=None):
        raise NotImplementedError


class ClipboardItemModule(ClipboardItemBase):
    key = constants.MODULE_KEY

    def _get_obj(self):
        return models.Module.objects.get(pk=self.pk).polymorph

    @property
    def contained_modules(self):
        return [self.obj]

    def duplicate(self, request, target_section=None):
        if target_section is None:
            new_section = models.Section.objects.create(container=self.target_container)
            self.obj.duplicate_to(new_section)
            return [self._render(request, self.xprez_admin, new_section)]
        else:
            new_module = self.obj.duplicate_to(target_section)
            return [self._render(request, self.xprez_admin, new_module)]

    def symlink(self, request, target_section=None):
        if target_section is None:
            new_section = models.Section.objects.create(container=self.target_container)
            models.ModuleSymlink.objects.create(section=new_section, symlink=self.obj)
            return [self._render(request, self.xprez_admin, new_section)]
        else:
            new_module = models.ModuleSymlink.objects.create(
                section=target_section, symlink=self.obj
            )
            return [self._render(request, self.xprez_admin, new_module)]


class ClipboardItemSection(ClipboardItemBase):
    key = constants.SECTION_KEY

    def _get_obj(self):
        return models.Section.objects.get(pk=self.pk)

    @property
    def allowed(self):
        if self.target_section is not None:
            return False
        else:
            return super().allowed

    @property
    def contained_modules(self):
        return self.obj.modules.filter(saved=True).polymorphs()

    def duplicate(self, request, target_section=None):
        new_section = self.obj.duplicate_to(
            self.target_container,
            allowed_module_classes=self.allowed_module_classes,
        )
        return [self._render(request, self.xprez_admin, new_section)]

    def symlink(self, request, target_section=None):
        new_symlink = self.obj.symlink_to(self.target_container)
        return [self._render(request, self.xprez_admin, new_symlink)]


class ClipboardItemContainer(ClipboardItemBase):
    key = constants.CONTAINER_KEY

    def _get_obj(self):
        return models.Container.objects.get(pk=self.pk).polymorph

    @property
    def allowed(self):
        if self.target_section is not None:
            return False
        else:
            return super().allowed

    @property
    def symlink_allowed(self):
        return not models.ContainerSymlink.would_create_cycle(
            self.target_container.pk, self.obj.pk
        )

    @property
    def contained_modules(self):
        return models.Module.objects.filter(
            section__container=self.obj,
            section__saved=True,
            saved=True,
        ).polymorphs()

    def duplicate(self, request, target_section=None):
        created = (
            self.obj.duplicate_to(
                self.target_container,
                allowed_module_classes=self.allowed_module_classes,
            )
            or []
        )
        return [self._render(request, self.xprez_admin, item) for item in created]

    def symlink(self, request, target_section=None):
        new_symlink = self.obj.symlink_to(self.target_container)
        return [self._render(request, self.xprez_admin, new_symlink)]


class XprezAdminViewsClipboardMixin:
    CLIPBOARD_SESSION_KEY = "xprez_clipboard"
    CLIPBOARD_MAX_LENGTH = 10
    CLIPBOARD_ITEM_REGISTRY = {
        cls.key: cls
        for cls in [ClipboardItemModule, ClipboardItemSection, ClipboardItemContainer]
    }

    def xprez_duplicate_section_view(self, request, section_pk):
        section = get_object_or_404(models.Section, pk=section_pk)
        new_section = section.duplicate_to(section.container)
        new_section.build_admin_form(self)
        return JsonResponse(
            [{"html": new_section.render_admin({"request": request})}], safe=False
        )

    def xprez_duplicate_module_view(self, request, module_pk):
        module = get_object_or_404(models.Module, pk=module_pk).polymorph
        new_module = module.duplicate_to(module.section)
        new_module.build_admin_form(self)
        return JsonResponse(
            [{"html": new_module.render_admin({"request": request})}], safe=False
        )

    def xprez_clipboard_clip(self, request, key, pk):
        self._add_clipboard_entry(request, (key, int(pk)))
        return HttpResponse()

    def xprez_clipboard_remove(self, request, key, pk):
        self._remove_clipboard_entry(request, (key, int(pk)))
        return HttpResponse()

    def xprez_clipboard_paste(
        self, request, key, pk, action, target_container_pk, target_section_pk=None
    ):
        target_container = get_object_or_404(models.Container, pk=target_container_pk)
        if target_section_pk is not None:
            target_section = get_object_or_404(
                models.Section,
                pk=target_section_pk,
                container=target_container,
            )
        else:
            target_section = None
        item = self._clipboard_item(key, pk, target_container, target_section)
        if not item.allowed:
            return HttpResponseBadRequest()
        elif action == CLIPBOARD_DUPLICATE_ACTION:
            return JsonResponse(item.duplicate(request, target_section), safe=False)
        elif action == CLIPBOARD_SYMLINK_ACTION:
            if not item.symlink_allowed:
                return HttpResponseBadRequest()
            return JsonResponse(item.symlink(request, target_section), safe=False)
        else:
            return HttpResponseBadRequest()

    def xprez_clipboard_list(
        self, request, target_container_pk, target_section_pk=None
    ):
        target_container = get_object_or_404(models.Container, pk=target_container_pk)
        if target_section_pk is not None:
            target_section = get_object_or_404(
                models.Section,
                pk=target_section_pk,
                container=target_container,
            )
        else:
            target_section = None
        return render(
            request,
            "xprez/admin/includes/clipboard.html",
            {
                "clipboard": self._get_clipboard_items(
                    request, target_container, target_section
                )
            },
        )

    def xprez_duplicate_url_name(self):
        return self.xprez_admin_url_name("duplicate", include_namespace=True)

    def xprez_clipboard_clip_url_name(self):
        return self.xprez_admin_url_name("clipboard_clip", include_namespace=True)

    def xprez_clipboard_remove_url_name(self):
        return self.xprez_admin_url_name("clipboard_remove", include_namespace=True)

    def xprez_clipboard_paste_url_name(self):
        return self.xprez_admin_url_name("clipboard_paste", include_namespace=True)

    def xprez_clipboard_list_url_name(self):
        return self.xprez_admin_url_name("clipboard_list", include_namespace=True)

    def xprez_clipboard_is_empty(self, request):
        return not bool(request.session.get(self.CLIPBOARD_SESSION_KEY, False))

    def xprez_admin_urls(self):
        return [
            path(
                f"xprez-duplicate/{constants.SECTION_KEY}/<int:section_pk>/",
                self.xprez_admin_view(self.xprez_duplicate_section_view),
                name=self.xprez_admin_url_name("duplicate"),
            ),
            path(
                f"xprez-duplicate/{constants.MODULE_KEY}/<int:module_pk>/",
                self.xprez_admin_view(self.xprez_duplicate_module_view),
                name=self.xprez_admin_url_name("duplicate"),
            ),
            path(
                "xprez-clipboard-clip/<str:key>/<int:pk>/",
                self.xprez_admin_view(self.xprez_clipboard_clip),
                name=self.xprez_admin_url_name("clipboard_clip"),
            ),
            path(
                "xprez-clipboard-remove/<str:key>/<int:pk>/",
                self.xprez_admin_view(self.xprez_clipboard_remove),
                name=self.xprez_admin_url_name("clipboard_remove"),
            ),
            path(
                "xprez-clipboard-paste/<str:key>/<int:pk>/<str:action>/<int:target_container_pk>/",
                self.xprez_admin_view(self.xprez_clipboard_paste),
                name=self.xprez_admin_url_name("clipboard_paste"),
            ),
            path(
                "xprez-clipboard-paste/<str:key>/<int:pk>/<str:action>/<int:target_container_pk>/section:<int:target_section_pk>/",
                self.xprez_admin_view(self.xprez_clipboard_paste),
                name=self.xprez_admin_url_name("clipboard_paste"),
            ),
            path(
                "xprez-clipboard-list/<int:target_container_pk>/",
                self.xprez_admin_view(self.xprez_clipboard_list),
                name=self.xprez_admin_url_name("clipboard_list"),
            ),
            path(
                "xprez-clipboard-list/<int:target_container_pk>/section:<int:target_section_pk>/",
                self.xprez_admin_view(self.xprez_clipboard_list),
                name=self.xprez_admin_url_name("clipboard_list"),
            ),
        ]

    def _clipboard_item(self, key, pk, target_container, target_section=None):
        return self.CLIPBOARD_ITEM_REGISTRY[key](
            pk, self, target_container, target_section
        )

    def _normalize_entry(self, entry):
        """Normalize to list to match JSON session serialization."""
        return list(entry)

    def _add_clipboard_entry(self, request, entry):
        session_data = request.session.get(self.CLIPBOARD_SESSION_KEY, [])
        session_data.insert(0, self._normalize_entry(entry))
        request.session[self.CLIPBOARD_SESSION_KEY] = session_data[
            : self.CLIPBOARD_MAX_LENGTH
        ]

    def _remove_clipboard_entry(self, request, entry):
        session_data = request.session.get(self.CLIPBOARD_SESSION_KEY, [])
        request.session[self.CLIPBOARD_SESSION_KEY] = [
            e for e in session_data if e != self._normalize_entry(entry)
        ]

    def _get_clipboard_items(self, request, target_container, target_section=None):
        session_data = request.session.get(self.CLIPBOARD_SESSION_KEY, [])
        result = []
        for key, pk in session_data:
            try:
                item = self._clipboard_item(key, pk, target_container, target_section)
                _ = item.obj  # raises ObjectDoesNotExist if gone
                result += [item]
            except (ObjectDoesNotExist, KeyError):
                self._remove_clipboard_entry(request, (key, pk))
        return result
