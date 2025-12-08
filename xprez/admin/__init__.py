from django.apps import apps
from django.conf import settings as django_settings
from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import path, re_path
from django.views.decorators.csrf import csrf_exempt

from xprez import contents_manager, models, settings
from xprez.admin.views import XprezAdminViewsMixin


class XprezModelFormMixin(object):
    def __init__(self, data=None, files=None, instance=None, **kwargs):
        super().__init__(data=data, files=files, instance=instance, **kwargs)
        self.xprez_sections = []
        self.xprez_sections_all_valid = None
        if instance:
            sections = instance.sections.all()
            if data is None:
                sections = sections.filter(saved=True)
            else:
                ids = [int(id) for id in data.getlist("section-id")]
                sections = sections.filter(pk__in=ids)

            for section in sections:
                section.build_admin_form(self.xprez_admin, data, files)
                self.xprez_sections.append(section)

    def is_valid(self):
        self.xprez_sections_all_valid = True
        for section in self.xprez_sections:
            if not section.is_admin_form_valid():
                self.xprez_sections_all_valid = False
        return super().is_valid() and self.xprez_sections_all_valid

    def xprez_save(self, request):
        for section in self.xprez_sections:
            if section.admin_form.cleaned_data.get("delete"):
                section.delete()
            else:
                section.saved = True
                section.save_admin_form(request)

        # TODO: think about this. What is the best way to delete old sections/contents?
        # for section in self.instance.sections.exclude(
        #     pk__in=[s.id for s in self.xprez_sections]
        # ).filter(saved=False, date_created__lt=timezone.now() - timedelta(days=5)):
        #     section.delete()

    def is_multipart(self):
        return True

    def xprez_get_allowed_contents(self):
        return self.xprez_admin.xprez_get_allowed_contents(container=self.instance)

    # TODO: remove, not used ... ?
    # def xprez_clipboard_list(self, request):
    #     return self.xprez_admin.xprez_clipboard_list(request, container=self.instance)


class XprezAdminMixin(XprezAdminViewsMixin):
    allowed_contents = settings.XPREZ_DEFAULT_ALLOWED_CONTENTS
    excluded_contents = settings.XPREZ_DEFAULT_EXCLUDED_CONTENTS

    def xprez_get_form(self, ModelForm=None):
        ModelForm = ModelForm or self.model_form

        class Form(XprezModelFormMixin, ModelForm):
            xprez_admin = self

        return Form

    def xprez_admin_media(self):
        return contents_manager.admin_media()

    def xprez_get_allowed_content_types(self, container):
        return [c.__name__.lower() for c in self.xprez_get_allowed_contents(container)]

    def xprez_get_allowed_contents(self, container):
        return contents_manager._get_allowed_contents(
            allowed_contents=self.allowed_contents,
            excluded_contents=self.excluded_contents,
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

        """
        admin's list_editable bypasses overrided get_form
        so it does not have save_xprez
        """
        if hasattr(form, "xprez_save"):
            form.xprez_save(request)

    @property
    def media(self, *args, **kwargs):
        return super().media + self.xprez_admin_media()

    def render_change_form(self, request, context, *args, **kwargs):
        context["errors"] = (
            context["errors"]
            or context["adminform"].form.xprez_sections_all_valid is False
        )
        return super().render_change_form(request, context, *args, **kwargs)

    def get_urls(self):
        return self.xprez_admin_urls() + super().get_urls()
