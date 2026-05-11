from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import render
from django.urls import path, reverse

from xprez import models
from xprez.admin.views.clipboard import ClipboardItemContainer


class XprezAdminViewsTemplateContainerMixin:
    def xprez_templatecontainers(self, container):
        return models.TemplateContainer.objects.filter(sections__saved=True).distinct()

    def xprez_templatecontainer_list_url_name(self):
        return self.xprez_admin_url_name(
            "templatecontainer_list", include_namespace=True
        )

    def xprez_templatecontainer_paste_url_name(self):
        return self.xprez_admin_url_name(
            "templatecontainer_paste", include_namespace=True
        )

    def xprez_templatecontainer_symlink_url_name(self):
        return self.xprez_admin_url_name(
            "templatecontainer_symlink", include_namespace=True
        )

    def xprez_templatecontainer_list_view(self, request, target_container_pk):
        target_container = self._get_container_instance(request, target_container_pk)
        items = []
        for template in self.xprez_templatecontainers(target_container):
            clipboard_item = ClipboardItemContainer(template.pk, self, target_container)
            url_args = [template.pk, target_container_pk]
            items += [
                {
                    "template": template,
                    "paste_url": reverse(
                        self.xprez_templatecontainer_paste_url_name(),
                        args=url_args,
                    ),
                    "symlink_url": reverse(
                        self.xprez_templatecontainer_symlink_url_name(),
                        args=url_args,
                    ),
                    "allowed": clipboard_item.allowed,
                    "symlink_allowed": clipboard_item.symlink_allowed,
                }
            ]
        return render(
            request,
            "xprez/admin/includes/templatecontainer_list.html",
            {"items": items},
        )

    def xprez_templatecontainer_paste_view(
        self, request, template_pk, target_container_pk
    ):
        target_container = self._get_container_instance(request, target_container_pk)
        clipboard_item = ClipboardItemContainer(template_pk, self, target_container)
        if not clipboard_item.allowed:
            return HttpResponseBadRequest()
        return JsonResponse(clipboard_item.duplicate(request), safe=False)

    def xprez_templatecontainer_symlink_view(
        self, request, template_pk, target_container_pk
    ):
        target_container = self._get_container_instance(request, target_container_pk)
        clipboard_item = ClipboardItemContainer(template_pk, self, target_container)
        if not clipboard_item.allowed or not clipboard_item.symlink_allowed:
            return HttpResponseBadRequest()
        return JsonResponse(clipboard_item.symlink(request), safe=False)

    def xprez_admin_urls(self):
        return [
            path(
                "xprez-templatecontainer-list/<int:target_container_pk>/",
                self.xprez_admin_view(self.xprez_templatecontainer_list_view),
                name=self.xprez_admin_url_name("templatecontainer_list"),
            ),
            path(
                "xprez-templatecontainer-paste/<int:template_pk>/<int:target_container_pk>/",
                self.xprez_admin_view(self.xprez_templatecontainer_paste_view),
                name=self.xprez_admin_url_name("templatecontainer_paste"),
            ),
            path(
                "xprez-templatecontainer-symlink/<int:template_pk>/<int:target_container_pk>/",
                self.xprez_admin_view(self.xprez_templatecontainer_symlink_view),
                name=self.xprez_admin_url_name("templatecontainer_symlink"),
            ),
        ]
