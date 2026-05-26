from django.db import transaction
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import include, path

from xprez import constants, models, module_registry
from xprez.conf import settings


class XprezAdminViewsContentMixin:
    def _xprez_create_section(self, container, content_type=None):
        section_defaults = settings.XPREZ_DEFAULTS["section"].get(content_type, {})
        section = models.Section(container=container, **section_defaults)
        section.save()
        return section

    def _xprez_create_module(self, module_class, section):
        module = module_class.build()
        module.section = section
        module.save()
        return module

    @transaction.atomic
    def xprez_add_view(self, request, container_pk, section_pk=None, content_type=None):
        """Add content to a container.

        Modes by URL kwargs:
        - only `container_pk`: create an empty section
        - `container_pk` + `content_type`: create a section containing the module
        - `container_pk` + `section_pk` + `content_type`: add module to that section
        """
        container = self._get_container_instance(request, container_pk)
        module_class = None
        if content_type is not None:
            try:
                module_class = module_registry.get(content_type)
            except LookupError as e:
                raise Http404 from e

        if module_class is None:
            renderable = self._xprez_create_section(container)
        elif section_pk is None:
            renderable = self._xprez_create_section(container, content_type)
            self._xprez_create_module(module_class, renderable)
        else:
            section = get_object_or_404(container.sections, pk=section_pk)
            renderable = self._xprez_create_module(module_class, section)

        renderable.build_admin_form(self)
        return JsonResponse(
            [{"html": renderable.render_admin({"request": request})}], safe=False
        )

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
                "xprez-add/<int:container_pk>/",
                include(
                    [
                        path(
                            "new-section/empty/",
                            self.xprez_admin_view(self.xprez_add_view),
                            name=self.xprez_admin_url_name("add"),
                        ),
                        path(
                            "new-section/<str:content_type>/",
                            self.xprez_admin_view(self.xprez_add_view),
                            name=self.xprez_admin_url_name("add"),
                        ),
                        path(
                            "<int:section_pk>/<str:content_type>/",
                            self.xprez_admin_view(self.xprez_add_view),
                            name=self.xprez_admin_url_name("add"),
                        ),
                    ]
                ),
            ),
            path(
                "xprez-config-add/",
                include(
                    [
                        path(
                            f"{constants.SECTION_KEY}/<int:section_pk>/<int:css_breakpoint>/",
                            self.xprez_admin_view(self.xprez_add_section_config_view),
                            name=self.xprez_admin_url_name("add_config"),
                        ),
                        path(
                            f"{constants.MODULE_KEY}/<int:module_pk>/<int:css_breakpoint>/",
                            self.xprez_admin_view(self.xprez_add_module_config_view),
                            name=self.xprez_admin_url_name("add_config"),
                        ),
                    ]
                ),
            ),
        ]
