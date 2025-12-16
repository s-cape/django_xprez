from django.apps import apps
from django.contrib import admin

from xprez import module_type_manager, settings
from xprez.admin.views.clipboard import XprezAdminViewsClipboardMixin
from xprez.admin.views.modules import XprezAdminViewsModulesMixin


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
        sections_to_delete = []
        for section in self.xprez_sections:
            if section.admin_form.cleaned_data.get("delete"):
                # do not delete yet, may contain modules to-be moved to other sections
                sections_to_delete += [section]
            else:
                section.saved = True
            section.save_admin_form(request)

        for section in sections_to_delete:
            section.delete()

    def is_multipart(self):
        return True

    def xprez_get_allowed_modules(self):
        return self.xprez_admin.xprez_get_allowed_modules(container=self.instance)


class XprezAdminMixin(XprezAdminViewsModulesMixin, XprezAdminViewsClipboardMixin):
    allowed_modules = settings.XPREZ_DEFAULT_ALLOWED_MODULES
    excluded_modules = settings.XPREZ_DEFAULT_EXCLUDED_MODULES

    xprez_breakpoints = settings.XPREZ_BREAKPOINTS
    xprez_default_breakpoint = settings.XPREZ_DEFAULT_BREAKPOINT

    def xprez_get_form(self, ModelForm=None):
        ModelForm = ModelForm or self.model_form

        class Form(XprezModelFormMixin, ModelForm):
            xprez_admin = self

        return Form

    def xprez_admin_media(self):
        return module_type_manager.admin_media()

    def xprez_get_allowed_module_types(self, container):
        return [m.__name__.lower() for m in self.xprez_get_allowed_modules(container)]

    def xprez_get_allowed_modules(self, container):
        return module_type_manager._get_allowed_modules(
            allowed_modules=self.allowed_modules,
            excluded_modules=self.excluded_modules,
        )

    xprez_url_namespace = None

    def xprez_admin_view(self, view):
        return view

    def xprez_admin_url_name(self, name, include_namespace=False):
        name = "{}_{}".format(self.model._meta.model_name, name)
        if include_namespace and self.xprez_url_namespace:
            name = "{}:{}".format(self.xprez_url_namespace, name)
        return name

    def xprez_admin_urls(self):
        urls = []
        urls += XprezAdminViewsModulesMixin.xprez_admin_urls(self)
        urls += XprezAdminViewsClipboardMixin.xprez_admin_urls(self)
        urls += module_type_manager.get_urls()
        return urls

    def _get_container_instance(self, request, object_pk):
        app_label, model_name = settings.XPREZ_CONTAINER_MODEL_CLASS.split(".")
        klass = apps.get_model(app_label, model_name)
        return klass.objects.get(pk=object_pk)

    def _updated_modules_positions(self, container):
        return {m.id: m.position for m in container.modules.all()}


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
