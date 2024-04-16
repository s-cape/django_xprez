from django.apps import apps
from django.conf import settings as django_settings
from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import path, re_path
from django.views.decorators.csrf import csrf_exempt

from . import contents_manager, models, settings


class XprezModelFormMixin(object):
    def __init__(self, data=None, files=None, instance=None, *args, **kwargs):
        super().__init__(data=data, files=files, instance=instance, *args, **kwargs)
        self.xprez_contents = []
        self.xprez_contents_all_valid = None
        if instance:
            for content in instance.contents.all():
                content = content.polymorph()
                content.build_admin_form(self.xprez_admin, data, files)
                self.xprez_contents.append(content)

    def is_valid(self):
        self.xprez_contents_all_valid = True
        for content in self.xprez_contents:
            if not content.is_admin_form_valid():
                self.xprez_contents_all_valid = False

        return super().is_valid() and self.xprez_contents_all_valid

    def save_xprez_contents(self, request):
        for content in self.xprez_contents:
            content.save_admin_form(request)

    def is_multipart(self):
        return True

    def xprez_get_allowed_contents(self):
        return self.xprez_admin.xprez_get_allowed_contents(container=self.instance)

    def xprez_clipboard_list(self, request):
        return self.xprez_admin.xprez_clipboard_list(request, container=self.instance)


class XprezAdminMixin(object):
    allowed_contents = settings.XPREZ_DEFAULT_ALLOWED_CONTENTS
    excluded_contents = settings.XPREZ_DEFAULT_EXCLUDED_CONTENTS

    def xprez_get_form(self, ModelForm=None):
        ModelForm = ModelForm or self.model_form

        class Form(XprezModelFormMixin, ModelForm):
            xprez_admin = self

        return Form

    def xprez_admin_media(self):
        return contents_manager.admin_media()

    def xprez_get_allowed_contents(self, container):
        return contents_manager._get_allowed_contents(
            allowed_contents=self.allowed_contents,
            excluded_contents=self.excluded_contents,
        )

    def xprez_ui_css_class(self):
        if "suit" in django_settings.INSTALLED_APPS:
            return "suit"
        elif "grapelli" in django_settings.INSTALLED_APPS:
            return "grapelli"
        return "default-admin"

    def _get_container_instance(self, request, object_pk):
        app_label, model_name = settings.XPREZ_CONTAINER_MODEL_CLASS.split(".")
        klass = apps.get_model(app_label, model_name)
        return klass.objects.get(pk=object_pk)

    def xprez_admin_view(self, view):
        return view

    xprez_url_namespace = None

    def xprez_admin_url_name(self, name, include_namespace=False):
        name = "{}_{}".format(self.model._meta.model_name, name)
        if include_namespace and self.xprez_url_namespace:
            name = "{}:{}".format(self.xprez_url_namespace, name)
        return name

    def xprez_add_content_url_name(self):
        return self.xprez_admin_url_name("add_content", include_namespace=True)

    def xprez_add_content_before_url_name(self):
        return self.xprez_admin_url_name("add_content_before", include_namespace=True)

    def xprez_delete_content_url_name(self):
        return self.xprez_admin_url_name("delete_content", include_namespace=True)

    def xprez_copy_content_url_name(self):
        return self.xprez_admin_url_name("copy_content", include_namespace=True)

    def xprez_copy_url_name(self):
        return self.xprez_admin_url_name("copy", include_namespace=True)

    def xprez_clipboard_copy_url_name(self):
        return self.xprez_admin_url_name("clipboard_copy", include_namespace=True)

    def xprez_clipboard_paste_url_name(self):
        return self.xprez_admin_url_name("clipboard_paste", include_namespace=True)

    def xprez_clipboard_list_url_name(self):
        return self.xprez_admin_url_name("clipboard_list", include_namespace=True)

    POSITION_CONTENT_BEFORE = "content_before"
    POSITION_CONTAINER_END = "container_end"

    CLIPBOARD_SESSION_KEY = "xprez_clipboard"
    CLIPBOARD_MAX_LENGTH = 10
    CLIPBOARD_CONTAINER_KEY = "container"
    CLIPBOARD_CONTENT_KEY = "content"

    CLIPBOARD_PASTE_ACTION = "paste"
    CLIPBOARD_SYMLINK_ACTION = "symlink"

    def xprez_admin_urls(self):
        urls = [
            path(
                "xprez-add-content/<int:page_pk>/<str:content_type>/",
                self.xprez_admin_view(self.xprez_add_content_view),
                name=self.xprez_admin_url_name("add_content"),
            ),
            path(
                "xprez-add-content-before/<int:before_content_pk>/<str:content_type>/",
                self.xprez_admin_view(self.xprez_add_content_before_view),
                name=self.xprez_admin_url_name("add_content_before"),
            ),
            path(
                "xprez-delete-content/<int:content_pk>/",
                self.xprez_admin_view(self.xprez_delete_content_view),
                name=self.xprez_admin_url_name("delete_content"),
            ),
            path(
                "xprez-copy-content/<int:content_pk>/",
                self.xprez_admin_view(self.xprez_copy_content_view),
                name=self.xprez_admin_url_name("copy_content"),
            ),
            re_path(
                r"^xprez-clipboard-copy/(?P<key>{}|{})/(?P<pk>[0-9]+)/$".format(
                    self.CLIPBOARD_CONTENT_KEY, self.CLIPBOARD_CONTAINER_KEY
                ),
                self.xprez_admin_view(self.xprez_clipboard_copy),
                name=self.xprez_admin_url_name("clipboard_copy"),
            ),
            re_path(
                r"^xprez-clipboard-paste/(?P<key>{}|{})/(?P<pk>[0-9]+)/(?P<action>{}|{})/(?P<target_position>{}|{})/(?P<target_pk>[0-9]+)/$".format(
                    self.CLIPBOARD_CONTENT_KEY,
                    self.CLIPBOARD_CONTAINER_KEY,
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
        if self.xprez_copy_supported():
            urls += [
                path(
                    "xprez-copy/<int:page_pk>/",
                    self.xprez_admin_view(self.xprez_copy_view),
                    name=self.xprez_admin_url_name("copy"),
                ),
            ]
        urls += contents_manager.get_urls()

        return urls

    def xprez_add_content_view(self, request, page_pk, content_type):
        content_class = contents_manager.get(content_type)

        container = self._get_container_instance(request, page_pk)
        content = content_class.create_for_page(container)
        content.build_admin_form(self)
        return JsonResponse(
            {
                "template": content.render_admin({"request": request}),
                "content_pk": content.pk,
            }
        )

    def xprez_add_content_before_view(self, request, before_content_pk, content_type):
        content_class = contents_manager.get(content_type)

        before_content = models.Content.objects.get(pk=before_content_pk)
        container = before_content.page
        content = content_class.create_for_page(
            container, position=before_content.position
        )
        content.build_admin_form(self)

        return JsonResponse(
            {
                "template": content.render_admin({"request": request}),
                "content_pk": content.pk,
                "updated_content_positions": self._updated_contents_positions(
                    container
                ),
            }
        )

    @csrf_exempt
    def xprez_delete_content_view(self, request, content_pk):
        if request.method == "POST":
            content = models.Content.objects.get(pk=content_pk)
            content.delete()
        return HttpResponse()

    def _updated_contents_positions(self, page):
        return dict([(c.id, c.position) for c in page.contents.all()])

    def xprez_copy_content_view(self, request, content_pk):
        content = models.Content.objects.get(pk=content_pk).polymorph()
        new_content = content.copy(position=content.position + 1)
        new_content.build_admin_form(self)

        return JsonResponse(
            {
                "template": new_content.render_admin({"request": request}),
                "content_pk": new_content.pk,
                "updated_content_positions": self._updated_contents_positions(
                    content.page
                ),
            }
        )

    def xprez_copy_supported(self):
        return hasattr(self.model, "copy")

    def xprez_copy_view(self, request, page_pk):
        inst = self.model.objects.get(pk=page_pk)
        copy = inst.copy()
        info = (copy._meta.app_label, copy._meta.model_name)
        return redirect("admin:%s_%s_change" % info, copy.pk)

    def xprez_clipboard_copy(self, request, key, pk):
        clipboard = request.session.get(self.CLIPBOARD_SESSION_KEY, [])
        clipboard.insert(0, (key, int(pk)))
        clipboard = clipboard[: self.CLIPBOARD_MAX_LENGTH]
        request.session[self.CLIPBOARD_SESSION_KEY] = clipboard
        return HttpResponse()

    def xprez_clipboard_paste(
        self, request, key, pk, action, target_position, target_pk
    ):
        if key == self.CLIPBOARD_CONTENT_KEY:
            contents = models.Content.objects.filter(pk=int(pk))
        elif key == self.CLIPBOARD_CONTAINER_KEY:
            contents = self._get_container_instance(request, int(pk)).contents.all()

        if target_position == self.POSITION_CONTENT_BEFORE:
            before_content = models.Content.objects.get(pk=target_pk)
            container = before_content.page
            position = before_content.position
        elif target_position == self.POSITION_CONTAINER_END:
            container = self._get_container_instance(request, target_pk)
            position = None

        contents_data = []
        for content in contents:
            if action == self.CLIPBOARD_PASTE_ACTION:
                new_content = content.polymorph().copy(
                    for_page=container, position=position
                )
            elif action == self.CLIPBOARD_SYMLINK_ACTION:
                # TODO
                pass
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

        clipboard = []
        for key, pk in session_data:
            try:
                if key == self.CLIPBOARD_CONTAINER_KEY:
                    obj = self._get_container_instance(request, pk).polymorph()
                elif key == self.CLIPBOARD_CONTENT_KEY:
                    obj = models.Content.objects.get(pk=pk).polymorph()

                clipboard += [
                    {
                        "key": key,
                        "obj": obj,
                    }
                ]
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


class XprezAdmin(XprezAdminMixin, admin.ModelAdmin):
    change_form_extend_template = "admin/change_form.html"
    change_form_template = "xprez/admin/xprez_changeform.html"

    @property
    def xprez_url_namespace(self):
        return self.admin_site.name

    def xprez_admin_view(self, view):
        return self.admin_site.admin_view(view)

    def get_form(self, *args, **kwargs):
        return self.xprez_get_form(super().get_form(*args, **kwargs))

    def save_model(self, request, obj, form, *args, **kwargs):
        super().save_model(request, obj, form, *args, **kwargs)
        form.save_xprez_contents(request)

    @property
    def media(self, *args, **kwargs):
        return super().media + self.xprez_admin_media()

    def render_change_form(self, request, context, *args, **kwargs):
        context["errors"] = (
            context["errors"]
            or context["adminform"].form.xprez_contents_all_valid is False
        )
        return super().render_change_form(request, context, *args, **kwargs)

    def get_urls(self):
        return self.xprez_admin_urls() + super().get_urls()
