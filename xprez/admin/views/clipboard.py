from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import re_path
from django.views.decorators.csrf import csrf_exempt

from xprez import models


class XprezAdminViewsClipboardMixin(object):
    POSITION_MODULE_BEFORE = "module_before"
    POSITION_SECTION_BEFORE = "section_before"
    POSITION_SECTION_END = "section_end"
    POSITION_CONTAINER_END = "container_end"

    CLIPBOARD_SESSION_KEY = "xprez_clipboard"
    CLIPBOARD_MAX_LENGTH = 10
    CLIPBOARD_CONTAINER_KEY = "container"
    CLIPBOARD_SECTION_KEY = "section"
    CLIPBOARD_MODULE_KEY = "module"

    CLIPBOARD_PASTE_ACTION = "paste"
    CLIPBOARD_SYMLINK_ACTION = "symlink"

    @csrf_exempt
    def xprez_clipboard_copy(self, request, key, pk):
        clipboard = request.session.get(self.CLIPBOARD_SESSION_KEY, [])
        clipboard.insert(0, (key, int(pk)))
        clipboard = clipboard[: self.CLIPBOARD_MAX_LENGTH]
        request.session[self.CLIPBOARD_SESSION_KEY] = clipboard
        return HttpResponse()

    def _xprez_target_container_and_position(self, request, target_position, target_pk):
        if target_position == self.POSITION_MODULE_BEFORE:
            before_module = models.Module.objects.get(pk=target_pk)
            return before_module.container, before_module.position
        elif target_position == self.POSITION_CONTAINER_END:
            return self._get_container_instance(request, target_pk), None

    @csrf_exempt
    def xprez_clipboard_paste(
        self, request, key, pk, action, target_position, target_pk
    ):
        if key == self.CLIPBOARD_MODULE_KEY:
            modules = models.Module.objects.filter(pk=int(pk))
        elif key == self.CLIPBOARD_CONTAINER_KEY:
            modules = self._get_container_instance(request, int(pk)).modules.all()

        container, position = self._xprez_target_container_and_position(
            request, target_position, target_pk
        )

        available_modules = self.xprez_get_available_modules(container)

        modules_data = []
        for module in modules:
            source_module = module.polymorph
            if source_module.__class__ not in available_modules:
                continue

            if action == self.CLIPBOARD_PASTE_ACTION:
                new_module = source_module.copy(
                    for_container=container, position=position
                )
            elif action == self.CLIPBOARD_SYMLINK_ACTION:
                new_module = models.ModuleSymlink.create_for_container(
                    container, position=position, symlink=source_module
                )

            new_module.build_admin_form(self)
            modules_data += [
                {
                    "template": new_module.render_admin({"request": request}),
                    "module_pk": new_module.pk,
                }
            ]
            if position is not None:
                position += 1

        return JsonResponse(
            {
                "modules": modules_data,
                "updated_module_positions": self._updated_modules_positions(container),
            }
        )

    def xprez_clipboard_is_empty(self, request):
        return not bool(request.session.get(self.CLIPBOARD_SESSION_KEY, False))

    def xprez_clipboard_list(self, request, target_position, target_pk):
        session_data = request.session.get(self.CLIPBOARD_SESSION_KEY, [])

        target_container, position = self._xprez_target_container_and_position(
            request, target_position, target_pk
        )
        available_modules = self.xprez_get_available_modules(target_container)

        clipboard = []
        for key, pk in session_data:
            try:
                if key == self.CLIPBOARD_CONTAINER_KEY:
                    obj = self._get_container_instance(request, pk).polymorph
                    modules = obj.modules.all()
                    if any(m in available_modules for m in modules):
                        if all(m in available_modules for m in modules):
                            available = True
                        else:
                            available = "partial"
                    else:
                        available = False
                elif key == self.CLIPBOARD_MODULE_KEY:
                    obj = models.Module.objects.get(pk=pk).polymorph
                    available = obj.content_type in available_modules

                clipboard += [{"key": key, "obj": obj, "available": available}]
            except ObjectDoesNotExist:
                pass

        return render(
            request,
            "xprez/admin/includes/clipboard.html",
            {
                "xprez_admin": self,
                "clipboard": clipboard,
                "target_position": target_position,
                "target_pk": target_pk,
            },
        )

    def xprez_clipboard_copy_url_name(self):
        return self.xprez_admin_url_name("clipboard_copy", include_namespace=True)

    def xprez_clipboard_paste_url_name(self):
        return self.xprez_admin_url_name("clipboard_paste", include_namespace=True)

    def xprez_clipboard_list_url_name(self):
        return self.xprez_admin_url_name("clipboard_list", include_namespace=True)

    def xprez_admin_urls(self):
        return [
            re_path(
                r"^xprez-clipboard-copy/(?P<key>{}|{})/(?P<pk>[0-9]+)/$".format(
                    self.CLIPBOARD_MODULE_KEY, self.CLIPBOARD_CONTAINER_KEY
                ),
                self.xprez_admin_view(self.xprez_clipboard_copy),
                name=self.xprez_admin_url_name("clipboard_copy"),
            ),
            re_path(
                r"^xprez-clipboard-paste/(?P<key>{}|{}|{})/(?P<pk>[0-9]+)/(?P<action>{}|{})/(?P<target_position>{}|{})/(?P<target_pk>[0-9]+)/$".format(
                    self.CLIPBOARD_MODULE_KEY,
                    self.CLIPBOARD_CONTAINER_KEY,
                    self.CLIPBOARD_SECTION_KEY,
                    self.CLIPBOARD_PASTE_ACTION,
                    self.CLIPBOARD_SYMLINK_ACTION,
                    self.POSITION_MODULE_BEFORE,
                    self.POSITION_CONTAINER_END,
                ),
                self.xprez_admin_view(self.xprez_clipboard_paste),
                name=self.xprez_admin_url_name("clipboard_paste"),
            ),
            re_path(
                r"^xprez-clipboard-list/(?P<target_position>{}|{})/(?P<target_pk>[0-9]+)/$".format(
                    self.POSITION_MODULE_BEFORE,
                    self.POSITION_CONTAINER_END,
                ),
                self.xprez_admin_view(self.xprez_clipboard_list),
                name=self.xprez_admin_url_name("clipboard_list"),
            ),
        ]
