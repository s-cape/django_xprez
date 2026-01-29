from django.http import HttpResponse, JsonResponse
from django.urls import path

from xprez import models, module_registry


class XprezAdminViewsContentMixin(object):
    def xprez_add_view(self, request, content_type, container_pk, section_pk=None):
        """Adds a module. Create a section+module if section_pk is not provided."""
        module_class = module_registry.get(content_type)
        container = self._get_container_instance(request, container_pk)
        if section_pk is None:
            section = container.sections.create()
            module = module_class.objects.create(section=section)
            section.build_admin_form(self)
            return HttpResponse(section.render_admin({"request": request}))
        else:
            section = container.sections.get(pk=section_pk)
            module = module_class.objects.create(section=section)
            module.build_admin_form(self)
            return HttpResponse(module.render_admin({"request": request}))

    def xprez_add_section_config_view(self, request, section_pk, css_breakpoint):
        section = models.Section.objects.get(pk=section_pk)
        config, _created = section.get_or_create_config(css_breakpoint)
        config.build_admin_form(self)
        return HttpResponse(config.render_admin({"request": request}))

    def xprez_add_module_config_view(self, request, module_pk, css_breakpoint):
        module = models.Module.objects.get(pk=module_pk).polymorph
        config, _created = module.get_or_create_config(css_breakpoint)
        config.build_admin_form(self)
        return HttpResponse(config.render_admin({"request": request}))

    def xprez_copy_module_view(self, request, module_pk):
        module = models.Module.objects.get(pk=module_pk).polymorph
        new_module = module.copy(position=module.position + 1)
        new_module.build_admin_form(self)

        return JsonResponse(
            {
                "template": new_module.render_admin({"request": request}),
                "module_pk": new_module.pk,
                "updated_module_positions": self._updated_modules_positions(
                    module.container
                ),
            }
        )

    def xprez_add_url_name(self):
        return self.xprez_admin_url_name("add", include_namespace=True)

    def xprez_copy_module_url_name(self):
        return self.xprez_admin_url_name("copy_module", include_namespace=True)

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
                "xprez-copy-module/<int:module_pk>/",
                self.xprez_admin_view(self.xprez_copy_module_view),
                name=self.xprez_admin_url_name("copy_module"),
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
