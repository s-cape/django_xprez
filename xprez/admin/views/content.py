from django.db import transaction
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import path

from xprez import constants, models, module_registry
from xprez.conf import settings


class XprezAdminViewsContentMixin:
    def _xprez_create_section(self, content_type, container):
        section_defaults = settings.XPREZ_DEFAULTS["section"].get(content_type, {})
        section = models.Section(container=container, **section_defaults)
        section.save()
        return section

    def _xprez_create_module(self, module_class, section):
        module = module_class.build()
        module.section = section
        module.save()
        return module

    def xprez_add_view(self, request, content_type, container_pk, section_pk=None):
        """Adds a module. Create a section+module if section_pk is not provided."""
        try:
            module_class = module_registry.get(content_type)
        except LookupError as e:
            raise Http404 from e
        container = self._get_container_instance(request, container_pk)
        if section_pk is None:
            with transaction.atomic():
                section = self._xprez_create_section(content_type, container)
                self._xprez_create_module(module_class, section)
            section.build_admin_form(self)
            html = section.render_admin({"request": request})
        else:
            section = get_object_or_404(container.sections, pk=section_pk)
            module = self._xprez_create_module(module_class, section)
            module.build_admin_form(self)
            html = module.render_admin({"request": request})
        return JsonResponse([{"html": html}], safe=False)

    def xprez_add_section_config_view(self, request, section_pk, css_breakpoint):
        section = self._get_section_instance(request, section_pk)
        config, _created = section.get_or_create_config(css_breakpoint)
        config.build_admin_form(self)
        return JsonResponse(
            [{"html": config.render_admin({"request": request})}], safe=False
        )

    def xprez_add_module_config_view(self, request, module_pk, css_breakpoint):
        module = self._get_module_instance(request, module_pk).polymorph
        config, _created = module.get_or_create_config(css_breakpoint)
        config.build_admin_form(self)
        return JsonResponse(
            [{"html": config.render_admin({"request": request})}], safe=False
        )

    def xprez_add_url_name(self):
        return self.xprez_admin_url_name("add", include_namespace=True)

    def xprez_add_config_url_name(self):
        return self.xprez_admin_url_name("add_config", include_namespace=True)

    def xprez_admin_urls(self):
        return [
            path(
                "xprez-add/<str:content_type>/<int:container_pk>/<int:section_pk>/",
                self.xprez_admin_view(self.xprez_add_view),
                name=self.xprez_admin_url_name("add"),
            ),
            path(
                "xprez-add/<str:content_type>/<int:container_pk>/",
                self.xprez_admin_view(self.xprez_add_view),
                name=self.xprez_admin_url_name("add"),
            ),
            path(
                f"xprez-config-add/{constants.SECTION_KEY}/<int:section_pk>/<int:css_breakpoint>/",
                self.xprez_admin_view(self.xprez_add_section_config_view),
                name=self.xprez_admin_url_name("add_config"),
            ),
            path(
                f"xprez-config-add/{constants.MODULE_KEY}/<int:module_pk>/<int:css_breakpoint>/",
                self.xprez_admin_view(self.xprez_add_module_config_view),
                name=self.xprez_admin_url_name("add_config"),
            ),
        ]
