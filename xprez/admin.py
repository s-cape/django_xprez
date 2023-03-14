from django.apps import apps
from django.conf import settings as django_settings
from django.contrib import admin
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.urls import re_path
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
                content.build_admin_form(self, data, files)
                self.xprez_contents.append(content)

    def is_valid(self):
        self.xprez_contents_all_valid = True
        for content in self.xprez_contents:
            if not content.is_admin_form_valid():
                self.xprez_contents_all_valid = False

        return super().is_valid() and self.xprez_contents_all_valid


class XprezAdminMixin(object):
    allowed_contents = settings.XPREZ_DEFAULT_ALLOWED_CONTENTS
    excluded_contents = settings.XPREZ_DEFAULT_EXCLUDED_CONTENTS

    def get_form(self, *args, **kwargs):
        ModelForm = super().get_form(*args, **kwargs)

        admin = self

        class Form(XprezModelFormMixin, ModelForm):
            # TODO:jakub - reorganize this somehow
            def _get_allowed_contents(self, *args, **kwargs):
                return admin._get_allowed_contents(*args, **kwargs)

        return Form

    def save_model(self, request, obj, form, *args, **kwargs):
        super().save_model(request, obj, form, *args, **kwargs)
        for content in form.xprez_contents:
            content.save_admin_form(request)

    def render_change_form(self, request, context, *args, **kwargs):
        context.update(
            {
                "copy_url_name": "admin:" + self.model._meta.model_name + "_copy",
                "copy_supported": hasattr(context["original"], "copy"),
                "errors": context["errors"]
                or context["adminform"].form.xprez_contents_all_valid is False,
            }
        )

        return super().render_change_form(request, context, *args, **kwargs)

    def _xprez_admin_media(self):
        return contents_manager.admin_media()

    def _get_allowed_contents(self):
        return contents_manager._get_allowed_contents(
            allowed_contents=self.allowed_contents,
            excluded_contents=self.excluded_contents,
        )

    def _get_ui_css_class(self):
        if "suit" in django_settings.INSTALLED_APPS:
            return "suit"
        elif "grapelli" in django_settings.INSTALLED_APPS:
            return "grapelli"
        return "default-admin"

    def _get_container_instance(self, request, object_pk):
        app_label, model_name = settings.XPREZ_CONTAINER_MODEL_CLASS.split(".")
        klass = apps.get_model(app_label, model_name)
        return klass.objects.get(pk=object_pk)

    def _add_xprez_context(self, extra_context=None):
        if not extra_context:
            extra_context = {}
        extra_context.update(
            {
                "content_types": self._get_allowed_contents(),
                "contents_media": self._xprez_admin_media(),
                "ui_css_class": self._get_ui_css_class(),
            }
        )
        return extra_context

    def _xprez_admin_urls(self):
        return [
            re_path(
                r"^%s/copy/(?P<page_pk>\d+)/$" % self.model._meta.model_name,
                self.admin_site.admin_view(self.copy_view),
                name=self.model._meta.model_name + "_copy",
            ),
            re_path(
                r"^ajax/add-content/(?P<page_pk>\d+)/(?P<content_type>[A-z0-9-]+)/$",
                self.admin_site.admin_view(self.add_content_view),
                name="ajax_add_content",
            ),
            re_path(
                r"^ajax/add-content-before/(?P<before_content_pk>\d+)/(?P<content_type>[A-z0-9-]+)/$",
                self.admin_site.admin_view(self.add_content_before_view),
                name="ajax_add_content_before",
            ),
            re_path(
                r"^ajax/delete-content/(?P<content_pk>\d+)/$",
                self.admin_site.admin_view(self.delete_content_view),
                name="ajax_delete_content",
            ),
            re_path(
                r"^ajax/copy-content/(?P<content_pk>\d+)/$",
                self.admin_site.admin_view(self.copy_content_view),
                name="ajax_copy_content",
            ),
        ]

    def add_content_view(self, request, page_pk, content_type):
        content_class = contents_manager.get(content_type)

        container = self._get_container_instance(request, page_pk)
        content = content_class.create_for_page(container)
        content.build_admin_form(self)
        return JsonResponse(
            {"template": content.render_admin(), "content_pk": content.pk}
        )

    def add_content_before_view(self, request, before_content_pk, content_type):
        content_class = contents_manager.get(content_type)

        before_content = models.Content.objects.get(pk=before_content_pk)
        container = before_content.page
        content = content_class.create_for_page(
            container, position=before_content.position
        )
        content.build_admin_form(self)

        updated_contents_positions = dict(
            [(c.id, c.position) for c in container.contents.all()]
        )
        return JsonResponse(
            {
                "template": content.render_admin(),
                "content_pk": content.pk,
                "updated_content_positions": updated_contents_positions,
            }
        )

    def copy_content_view(self, request, content_pk):
        content = models.Content.objects.get(pk=content_pk).polymorph()
        new_content = content.copy()
        new_content.build_admin_form(self)
        return JsonResponse(
            {"template": new_content.render_admin(), "content_pk": new_content.pk}
        )

    def copy_view(self, request, page_pk):
        inst = self.model.objects.get(pk=page_pk)
        copy = inst.copy()
        info = (copy._meta.app_label, copy._meta.model_name)
        return redirect("admin:%s_%s_change" % info, copy.pk)

    @csrf_exempt
    def delete_content_view(self, request, content_pk):
        if request.method == "POST":
            content = models.Content.objects.get(pk=content_pk)
            content.delete()
        return HttpResponse()


class XprezAdmin(XprezAdminMixin, admin.ModelAdmin):
    change_form_extend_template = "admin/change_form.html"
    change_form_template = "xprez/admin/xprez_changeform.html"

    @property
    def media(self, *args, **kwargs):
        return super().media + self._xprez_admin_media()

    def _add_xprez_context(self, extra_context=None):
        context = super()._add_xprez_context(extra_context=extra_context)
        context.update(
            {"change_form_extend_template": self.change_form_extend_template}
        )
        return context

    def change_view(self, request, object_id, form_url="", extra_context=None):
        return super().change_view(
            request,
            object_id,
            form_url,
            extra_context=self._add_xprez_context(extra_context),
        )

    def add_view(self, request, form_url="", extra_context=None):
        return super().add_view(
            request, form_url, extra_context=self._add_xprez_context(extra_context)
        )

    def get_urls(self):
        return self._xprez_admin_urls() + super().get_urls()
