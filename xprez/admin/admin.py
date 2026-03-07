from django.apps import apps
from django.contrib import admin

from xprez import constants, module_registry, settings
from xprez.admin.views.clipboard import XprezAdminViewsClipboardMixin
from xprez.admin.views.content import XprezAdminViewsContentMixin
from xprez.media import AdminMediaCollector


class XprezModelFormMixin(object):
    def __init__(self, data=None, files=None, instance=None, **kwargs):
        super().__init__(data=data, files=files, instance=instance, **kwargs)
        self.xprez_sections = []
        self.xprez_sections_all_valid = None
        if instance:
            sections = instance.sections.all()
            section_symlinks = instance.sectionsymlinks.all()
            if data is None:
                sections = sections.filter(saved=True)
                section_symlinks = section_symlinks.filter(saved=True)
            else:
                section_ids = [int(id) for id in data.getlist("section-id")]
                section_symlink_ids = [
                    int(id) for id in data.getlist("section-symlink-id")
                ]
                sections = sections.filter(pk__in=section_ids)
                section_symlinks = section_symlinks.filter(pk__in=section_symlink_ids)

            for section in sections:
                section.build_admin_form(self.xprez_admin, data, files)
                self.xprez_sections.append(section)
            for section_symlink in section_symlinks:
                section_symlink.build_admin_form(self.xprez_admin, data, files)
                self.xprez_sections.append(section_symlink)
        self.xprez_sections.sort(key=lambda s: s.admin_form.get_position())

    def is_valid(self):
        self.xprez_sections_all_valid = True
        for section in self.xprez_sections:
            if not section.is_admin_form_valid():
                self.xprez_sections_all_valid = False
        return super().is_valid() and self.xprez_sections_all_valid

    def xprez_save(self, request):
        sections_to_delete = []
        for section in self.xprez_sections:
            if getattr(section.admin_form, "deleted", False):
                # do not delete yet, may contain modules to-be moved to other sections
                sections_to_delete += [section]
            section.save_admin_form(request)

        for section in sections_to_delete:
            section.delete()

    def is_multipart(self):
        return True

    def xprez_add_menu_module_classes(self):
        return self.xprez_admin.xprez_add_menu_module_classes(self.instance)


class XprezAdminMixin(
    XprezAdminViewsContentMixin,
    XprezAdminViewsClipboardMixin,
):
    constants = constants
    xprez_breakpoints = settings.XPREZ_BREAKPOINTS
    xprez_default_breakpoint = 0

    def xprez_get_form(self, ModelForm=None):
        ModelForm = ModelForm or self.model_form

        class Form(XprezModelFormMixin, ModelForm):
            xprez_admin = self

        return Form

    def xprez_admin_media(self):
        return AdminMediaCollector().get_media()

    def xprez_allowed_modules(self, container=None):
        return module_registry.allowed_modules()

    def xprez_add_menu_modules(self, container=None):
        allowed = set(self.xprez_allowed_modules(container))
        return [ct for ct in module_registry.add_menu_modules() if ct in allowed]

    def xprez_allowed_module_classes(self, container=None):
        return module_registry.module_classes(
            include=self.xprez_allowed_modules(container)
        )

    def xprez_add_menu_module_classes(self, container=None):
        return module_registry.module_classes(
            include=self.xprez_add_menu_modules(container)
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
        urls += XprezAdminViewsContentMixin.xprez_admin_urls(self)
        urls += XprezAdminViewsClipboardMixin.xprez_admin_urls(self)
        urls += module_registry.get_admin_urls()
        return urls

    def _get_container_instance(self, request, object_pk):
        cls = apps.get_model("xprez", "Container")
        return cls.objects.get(pk=object_pk)


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
