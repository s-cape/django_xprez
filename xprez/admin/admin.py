import functools

from django.contrib import admin
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from django.utils.html import format_html

from xprez import constants, models, module_registry, settings
from xprez.admin.permissions import xprez_staff_member_required
from xprez.admin.views.ckeditor_upload import XprezAdminViewsCkEditorUploadMixin
from xprez.admin.views.clipboard import XprezAdminViewsClipboardMixin
from xprez.admin.views.content import XprezAdminViewsContentMixin
from xprez.admin.views.template_container import XprezAdminViewsTemplateContainerMixin
from xprez.ck_editor.forms import CkEditorFileUploadXprezAdminFormMixin
from xprez.media import AdminMediaCollector


class XprezModelFormMixin:
    def __init__(self, data=None, files=None, instance=None, **kwargs):
        super().__init__(data=data, files=files, instance=instance, **kwargs)
        self.xprez_sections = []
        self.xprez_sections_all_valid = None
        if instance:
            sections = instance.sections.all()
            section_symlinks = instance.sectionsymlinks.all()
            container_symlinks = instance.containersymlinks.all()
            if data is not None:
                section_pks = [int(pk) for pk in data.getlist("section-id")]
                section_symlink_pks = [
                    int(pk) for pk in data.getlist("section-symlink-id")
                ]
                container_symlink_pks = [
                    int(pk) for pk in data.getlist("container-symlink-id")
                ]
                sections = sections.filter(pk__in=section_pks)
                section_symlinks = section_symlinks.filter(pk__in=section_symlink_pks)
                container_symlinks = container_symlinks.filter(
                    pk__in=container_symlink_pks
                )

            for section in sections:
                section.build_admin_form(self.xprez_admin, data, files)
                self.xprez_sections.append(section)
            for section_symlink in section_symlinks:
                section_symlink.build_admin_form(self.xprez_admin, data, files)
                self.xprez_sections.append(section_symlink)
            for container_symlink in container_symlinks:
                container_symlink.build_admin_form(self.xprez_admin, data, files)
                self.xprez_sections.append(container_symlink)
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
    XprezAdminViewsTemplateContainerMixin,
    XprezAdminViewsCkEditorUploadMixin,
):
    constants = constants
    xprez_breakpoints = settings.XPREZ_BREAKPOINTS
    xprez_default_breakpoint = 0

    def xprez_get_form(self, ModelForm=None):
        ModelForm = ModelForm or self.model_form

        class Form(
            XprezModelFormMixin, CkEditorFileUploadXprezAdminFormMixin, ModelForm
        ):
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
        """Default permission wrapper for xprez admin views.

        `XprezAdmin` overrides this with `admin_site.admin_view` (which is
        stricter). The default protects custom `XprezAdminMixin` consumers from
        accidentally exposing mutating endpoints to anonymous users.
        """
        return xprez_staff_member_required(view)

    def xprez_admin_module_view(self, view):
        """Wrap a module classmethod view, pre-binding `xprez_admin` as first arg."""
        return self.xprez_admin_view(functools.partial(view, self))

    def xprez_admin_url_name(self, name, include_namespace=False):
        name = f"{self.model._meta.model_name}_{name}"
        if include_namespace and self.xprez_url_namespace:
            name = f"{self.xprez_url_namespace}:{name}"
        return name

    def xprez_admin_urls(self):
        urls = []
        urls += XprezAdminViewsContentMixin.xprez_admin_urls(self)
        urls += XprezAdminViewsClipboardMixin.xprez_admin_urls(self)
        urls += XprezAdminViewsTemplateContainerMixin.xprez_admin_urls(self)
        urls += XprezAdminViewsCkEditorUploadMixin.xprez_admin_urls(self)
        urls += module_registry.get_admin_urls(self)
        return urls

    def xprez_admin_change_url(self, obj):
        """Change URL for `obj` in this admin site, or None if not registered."""
        try:
            return reverse(
                f"{self.xprez_url_namespace}:{obj._meta.app_label}_{obj._meta.model_name}_change",
                args=[obj.pk],
            )
        except NoReverseMatch:
            return None

    def xprez_get_container_qs(self, request):
        """Containers this admin is allowed to touch.

        Override to restrict admin endpoints to a per-request subset (e.g.
        when staff users only manage a subset of containers). All xprez admin
        endpoints that resolve a `*_container_pk` / `*_section_pk` /
        `*_module_pk` route through this queryset.
        """
        return self.model._default_manager.all()

    def _get_container_instance(self, request, object_pk):
        return get_object_or_404(self.xprez_get_container_qs(request), pk=object_pk)

    def _get_section_instance(self, request, section_pk):
        return get_object_or_404(
            models.Section.objects.filter(
                container__in=self.xprez_get_container_qs(request)
            ),
            pk=section_pk,
        )

    def _get_module_instance(self, request, module_pk, model=None):
        """Resolve `module_pk` scoped to this admin's containers.

        Pass `model` (a concrete `Module` subclass) to also constrain by type
        and get the concrete instance back without a separate `polymorph` query.
        """
        model = model or models.Module
        return get_object_or_404(
            model.objects.filter(
                section__container__in=self.xprez_get_container_qs(request)
            ),
            pk=module_pk,
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
        with transaction.atomic():
            super().save_model(request, obj, form, *args, **kwargs)
            # admin's list_editable bypasses overridden get_form, so it may not have xprez_save
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


class TemplateContainerAdmin(XprezAdmin):
    list_display = ("display_key", "image_preview", "description")
    search_fields = ("key", "description", "keywords")

    @admin.display(description="Image")
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:48px;">', obj.image.url)
        return ""
