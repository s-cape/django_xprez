from django.http import JsonResponse
from django.urls import path

from xprez import models, module_registry


class XprezAdminViewsContentMixin(object):
    def xprez_add_view(self, request, content_type, container_pk, section_pk=None):
        """Adds a module. Create a section+module if section_pk is not provided."""
        module_class = module_registry.get(content_type)
        container = self._get_container_instance(request, container_pk)
        if section_pk is None:
            section = container.sections.create()
            module_class.objects.create(section=section)
            section.build_admin_form(self)
            html = section.render_admin({"request": request})
        else:
            section = container.sections.get(pk=section_pk)
            module = module_class.objects.create(section=section)
            module.build_admin_form(self)
            html = module.render_admin({"request": request})
        return JsonResponse([{"html": html}], safe=False)

    def xprez_add_section_config_view(self, request, section_pk, css_breakpoint):
        section = models.Section.objects.get(pk=section_pk)
        config, _created = section.get_or_create_config(css_breakpoint)
        config.build_admin_form(self)
        return JsonResponse(
            [{"html": config.render_admin({"request": request})}], safe=False
        )

    def xprez_add_module_config_view(self, request, module_pk, css_breakpoint):
        module = models.Module.objects.get(pk=module_pk).polymorph
        config, _created = module.get_or_create_config(css_breakpoint)
        config.build_admin_form(self)
        return JsonResponse(
            [{"html": config.render_admin({"request": request})}], safe=False
        )

    def xprez_duplicate_section_view(self, request, section_pk):
        section = models.Section.objects.get(pk=section_pk)
        new_section = section.duplicate_to(section.container)
        new_section.build_admin_form(self)
        return JsonResponse(
            [{"html": new_section.render_admin({"request": request})}], safe=False
        )

    def xprez_duplicate_module_view(self, request, module_pk):
        module = models.Module.objects.get(pk=module_pk).polymorph
        new_module = module.duplicate_to(module.section)
        new_module.build_admin_form(self)
        return JsonResponse(
            [{"html": new_module.render_admin({"request": request})}], safe=False
        )

    def xprez_add_url_name(self):
        return self.xprez_admin_url_name("add", include_namespace=True)

    def xprez_duplicate_section_url_name(self):
        return self.xprez_admin_url_name("duplicate_section", include_namespace=True)

    def xprez_duplicate_module_url_name(self):
        return self.xprez_admin_url_name("duplicate_module", include_namespace=True)

    def xprez_add_section_config_url_name(self):
        return self.xprez_admin_url_name("add_section_config", include_namespace=True)

    def xprez_add_module_config_url_name(self):
        return self.xprez_admin_url_name("add_module_config", include_namespace=True)

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
                "xprez-duplicate-section/<int:section_pk>/",
                self.xprez_admin_view(self.xprez_duplicate_section_view),
                name=self.xprez_admin_url_name("duplicate_section"),
            ),
            path(
                "xprez-duplicate-module/<int:module_pk>/",
                self.xprez_admin_view(self.xprez_duplicate_module_view),
                name=self.xprez_admin_url_name("duplicate_module"),
            ),
            path(
                "section-config-add/<int:section_pk>/<int:css_breakpoint>/",
                self.xprez_admin_view(self.xprez_add_section_config_view),
                name=self.xprez_admin_url_name("add_section_config"),
            ),
            path(
                "module-config-add/<int:module_pk>/<int:css_breakpoint>/",
                self.xprez_admin_view(self.xprez_add_module_config_view),
                name=self.xprez_admin_url_name("add_module_config"),
            ),
        ]
