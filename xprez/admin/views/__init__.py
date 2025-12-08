from django.apps import apps

from xprez import contents_manager, settings

from .base import XprezAdminViewsBaseMixin
from .clipboard import XprezAdminViewsClipboardMixin


class XprezAdminViewsMixin(XprezAdminViewsBaseMixin, XprezAdminViewsClipboardMixin):
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
        urls += XprezAdminViewsBaseMixin.xprez_admin_urls(self)
        urls += XprezAdminViewsClipboardMixin.xprez_admin_urls(self)
        urls += contents_manager.get_urls()
        return urls

    def _get_container_instance(self, request, object_pk):
        app_label, model_name = settings.XPREZ_CONTAINER_MODEL_CLASS.split(".")
        klass = apps.get_model(app_label, model_name)
        return klass.objects.get(pk=object_pk)

    def _updated_contents_positions(self, container):
        return {c.id: c.position for c in container.contents.all()}
