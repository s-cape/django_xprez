from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import re_path
from django.views.decorators.csrf import csrf_exempt

from xprez import models


class XprezAdminViewsClipboardMixin(object):
    POSITION_CONTENT_BEFORE = "content_before"
    POSITION_SECTION_BEFORE = "section_before"
    POSITION_SECTION_END = "section_end"
    POSITION_CONTAINER_END = "container_end"

    CLIPBOARD_SESSION_KEY = "xprez_clipboard"
    CLIPBOARD_MAX_LENGTH = 10
    CLIPBOARD_CONTAINER_KEY = "container"
    CLIPBOARD_SECTION_KEY = "section"
    CLIPBOARD_CONTENT_KEY = "content"

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
        if target_position == self.POSITION_CONTENT_BEFORE:
            before_content = models.Content.objects.get(pk=target_pk)
            return before_content.container, before_content.position
        elif target_position == self.POSITION_CONTAINER_END:
            return self._get_container_instance(request, target_pk), None

    @csrf_exempt
    def xprez_clipboard_paste(
        self, request, key, pk, action, target_position, target_pk
    ):
        if key == self.CLIPBOARD_CONTENT_KEY:
            contents = models.Content.objects.filter(pk=int(pk))
        elif key == self.CLIPBOARD_CONTAINER_KEY:
            contents = self._get_container_instance(request, int(pk)).contents.all()

        container, position = self._xprez_target_container_and_position(
            request, target_position, target_pk
        )

        allowed_contents = self.xprez_get_allowed_contents(container)

        contents_data = []
        for content in contents:
            source_content = content.polymorph()
            if source_content.__class__ not in allowed_contents:
                continue

            if action == self.CLIPBOARD_PASTE_ACTION:
                new_content = source_content.copy(
                    for_container=container, position=position
                )
            elif action == self.CLIPBOARD_SYMLINK_ACTION:
                new_content = models.ContentSymlink.create_for_container(
                    container, position=position, symlink=source_content
                )

            new_content.build_admin_form(self)
            contents_data += [
                {
                    "template": new_content.render_admin({"request": request}),
                    "content_pk": new_content.pk,
                }
            ]
            if position is not None:
                position += 1

        return JsonResponse(
            {
                "contents": contents_data,
                "updated_content_positions": self._updated_contents_positions(
                    container
                ),
            }
        )

    def xprez_clipboard_is_empty(self, request):
        return not bool(request.session.get(self.CLIPBOARD_SESSION_KEY, False))

    def xprez_clipboard_list(self, request, target_position, target_pk):
        session_data = request.session.get(self.CLIPBOARD_SESSION_KEY, [])

        target_container, position = self._xprez_target_container_and_position(
            request, target_position, target_pk
        )
        allowed_content_types = self.xprez_get_allowed_content_types(target_container)

        clipboard = []
        for key, pk in session_data:
            try:
                if key == self.CLIPBOARD_CONTAINER_KEY:
                    obj = self._get_container_instance(request, pk).polymorph()
                    contents = obj.contents.all()
                    if any(c.content_type in allowed_content_types for c in contents):
                        if all(
                            c.content_type in allowed_content_types for c in contents
                        ):
                            allowed = True
                        else:
                            allowed = "partial"
                    else:
                        allowed = False
                elif key == self.CLIPBOARD_CONTENT_KEY:
                    obj = models.Content.objects.get(pk=pk).polymorph()
                    allowed = obj.content_type in allowed_content_types

                clipboard += [{"key": key, "obj": obj, "allowed": allowed}]
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
                    self.CLIPBOARD_CONTENT_KEY, self.CLIPBOARD_CONTAINER_KEY
                ),
                self.xprez_admin_view(self.xprez_clipboard_copy),
                name=self.xprez_admin_url_name("clipboard_copy"),
            ),
            re_path(
                r"^xprez-clipboard-paste/(?P<key>{}|{}|{})/(?P<pk>[0-9]+)/(?P<action>{}|{})/(?P<target_position>{}|{})/(?P<target_pk>[0-9]+)/$".format(
                    self.CLIPBOARD_CONTENT_KEY,
                    self.CLIPBOARD_CONTAINER_KEY,
                    self.CLIPBOARD_SECTION_KEY,
                    self.CLIPBOARD_PASTE_ACTION,
                    self.CLIPBOARD_SYMLINK_ACTION,
                    self.POSITION_CONTENT_BEFORE,
                    self.POSITION_CONTAINER_END,
                ),
                self.xprez_admin_view(self.xprez_clipboard_paste),
                name=self.xprez_admin_url_name("clipboard_paste"),
            ),
            re_path(
                r"^xprez-clipboard-list/(?P<target_position>{}|{})/(?P<target_pk>[0-9]+)/$".format(
                    self.POSITION_CONTENT_BEFORE,
                    self.POSITION_CONTAINER_END,
                ),
                self.xprez_admin_view(self.xprez_clipboard_list),
                name=self.xprez_admin_url_name("clipboard_list"),
            ),
        ]
