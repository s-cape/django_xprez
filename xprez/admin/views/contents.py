from django.http import HttpResponse, JsonResponse
from django.urls import path

from xprez import contents_manager, models


class XprezAdminViewsContentsMixin(object):
    def xprez_add_view(self, request, content_type, container_pk, section_pk=None):
        """Adds a content. Create a section+content if section_pk is not provided."""
        content_class = contents_manager.get(content_type)
        container = self._get_container_instance(request, container_pk)
        if section_pk is None:
            section = container.sections.create()
            content = content_class.objects.create(section=section)
            section.build_admin_form(self)
            return HttpResponse(section.render_admin({"request": request}))
        else:
            section = container.sections.get(pk=section_pk)
            content = content_class.objects.create(section=section)
            content.build_admin_form(self)
            return HttpResponse(content.render_admin({"request": request}))

    def xprez_copy_content_view(self, request, content_pk):
        content = models.Content.objects.get(pk=content_pk).polymorph()
        new_content = content.copy(position=content.position + 1)
        new_content.build_admin_form(self)

        return JsonResponse(
            {
                "template": new_content.render_admin({"request": request}),
                "content_pk": new_content.pk,
                "updated_content_positions": self._updated_contents_positions(
                    content.container
                ),
            }
        )

    def xprez_add_url_name(self):
        return self.xprez_admin_url_name("add", include_namespace=True)

    def xprez_copy_content_url_name(self):
        return self.xprez_admin_url_name("copy_content", include_namespace=True)

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
                "xprez-copy-content/<int:content_pk>/",
                self.xprez_admin_view(self.xprez_copy_content_view),
                name=self.xprez_admin_url_name("copy_content"),
            ),
        ]
