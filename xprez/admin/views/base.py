from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from xprez import contents_manager, models


class XprezAdminViewsBaseMixin(object):
    def xprez_add_view(self, request, content_type, container_pk, section_pk=None):
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

        # container = self._get_container_instance(request, pk)
        # content = content_class.create_for_container(container)
        # content.build_admin_form(self)
        # return JsonResponse(
        #     {
        #         "template": content.render_admin({"request": request}),
        #         "content_pk": content.pk,
        #     }
        # )

    #     container = self._get_container_instance(request, container_pk)
    #     content = content_class.create_for_container(container)
    #     content.build_admin_form(self)
    #     return JsonResponse(
    #         {
    #             "template": content.render_admin({"request": request}),
    #             "content_pk": content.pk,
    #         }
    #     )

    # def xprez_add_content_before_view(self, request, before_content_pk, content_type):
    #     content_class = contents_manager.get(content_type)

    #     before_content = models.Content.objects.get(pk=before_content_pk)
    #     container = before_content.container
    #     content = content_class.create_for_container(
    #         container, position=before_content.position
    #     )
    #     content.build_admin_form(self)

    #     return JsonResponse(
    #         {
    #             "template": content.render_admin({"request": request}),
    #             "content_pk": content.pk,
    #             "updated_content_positions": self._updated_contents_positions(
    #                 container
    #             ),
    #         }
    #     )

    @csrf_exempt
    def xprez_delete_content_view(self, request, content_pk):
        if request.method == "POST":
            content = models.Content.objects.get(pk=content_pk)
            content.delete()
        return HttpResponse()

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

    # def xprez_add_content_before_url_name(self):
    #     return self.xprez_admin_url_name("add_content_before", include_namespace=True)

    # def xprez_delete_content_url_name(self):
    #     return self.xprez_admin_url_name("delete_content", include_namespace=True)

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
            # path(
            #     "xprez-add-content/<str:content_type>/<int:container_pk>/",
            #     self.xprez_admin_view(self.xprez_add_content_before_view),
            #     name=self.xprez_admin_url_name("add_content"),
            # ),
            # re_path(
            #     r"^xprez-add-content/(?P<position>{}|{}|{})/(?P<pk>[0-9]+)/(?P<content_type>[A-Za-z_]+)/$".format(
            #         self.POSITION_SECTION_BEFORE,
            #         self.POSITION_SECTION_END,
            #         self.POSITION_CONTAINER_END,
            #     ),
            #     self.xprez_admin_view(self.xprez_add_content_view),
            #     name=self.xprez_admin_url_name("add_content"),
            # ),
            # path(
            #     "xprez-add-content-before/<int:before_content_pk>/<str:content_type>/",
            #     self.xprez_admin_view(self.xprez_add_content_before_view),
            #     name=self.xprez_admin_url_name("add_content_before"),
            # ),
            # path(
            #     "xprez-delete-content/<int:content_pk>/",
            #     self.xprez_admin_view(self.xprez_delete_content_view),
            #     name=self.xprez_admin_url_name("delete_content"),
            # ),
        ]
