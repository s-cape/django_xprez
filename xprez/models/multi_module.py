from django.db import models
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.urls import re_path
from django.utils.decorators import method_decorator

from xprez.admin.permissions import xprez_staff_member_required
from xprez.models.modules import Module
from xprez.utils import import_class


class MultiModule(Module):
    """Module with multiple child items managed via individual forms."""

    items_attribute = "items"
    admin_item_template_name = "xprez/admin/modules/multi_module/multi_module_item.html"
    admin_item_form_class = "xprez.admin.forms.MultiModuleItemForm"
    admin_js_controller_class = "XprezMultiModule"
    admin_item_js_controller_class = "XprezMultiModuleItem"

    def get_admin_item_form_class(self, item):
        cls = import_class(self.admin_item_form_class)
        if cls._meta.model:
            return cls

        class ItemForm(cls):
            class Meta(cls.Meta):
                model = item.__class__

        return ItemForm

    def render_front(self, context):
        items = (
            getattr(self, self.items_attribute).filter(saved=True).order_by("position")
        )
        if not items.exists():
            return ""
        context = {**context, "items": items}
        return super().render_front(context)

    def get_items_queryset(self, data=None):
        qs = getattr(self, self.items_attribute)
        if data is None:
            return qs.filter(saved=True).order_by("position")
        ids = [int(id) for id in data.getlist(f"{self.key}-item-id")]
        items = list(qs.filter(pk__in=ids))
        items.sort(key=lambda item: ids.index(item.pk))
        return items

    def build_admin_form(self, admin, data=None, files=None):
        super().build_admin_form(admin, data, files)
        items = self.get_items_queryset(data)
        self.admin_form.xprez_items = []
        for item in items:
            form_class = self.get_admin_item_form_class(item)
            item.admin_form = form_class(
                instance=item, prefix=item.key, data=data, files=files
            )
            self.admin_form.xprez_items += [item]

    def save_admin_form(self, request):
        super().save_admin_form(request)
        for index, item in enumerate(self.admin_form.xprez_items):
            if (item.admin_form.cleaned_data or {}).get("delete"):
                item.delete()
            else:
                inst = item.admin_form.save(commit=False)
                inst.saved = True
                inst.position = index
                inst.save()

    def is_admin_form_valid(self):
        items_valid = all(
            item.admin_form.is_valid() for item in self.admin_form.xprez_items
        )
        return super().is_admin_form_valid() and items_valid

    def admin_has_errors(self):
        items_errors = any(
            item.admin_form.errors for item in self.admin_form.xprez_items
        )
        return super().admin_has_errors() or items_errors

    def build_item(self):
        item_model = getattr(self, self.items_attribute).model
        return item_model(**{item_model.module_foreign_key: self})

    def create_item(self, saved=False):
        item = self.build_item()
        item.saved = saved
        item.save()
        return item

    def copy(self, for_container=None, save=True, position=None):
        inst = super().copy(for_container, save=save, position=position)
        if save:
            self.copy_items(inst)
        return inst

    def copy_items(self, inst):
        for item in getattr(self, self.items_attribute).filter(saved=True):
            item.copy(inst)

    @classmethod
    def get_admin_urls(cls):
        cls_name = cls.__name__.lower()
        return [
            re_path(
                r"^{}/add-item/(?P<module_pk>\d+)/".format(cls_name),
                cls.add_item_view,
                name=cls.get_add_item_url_name(),
            ),
        ]

    @classmethod
    @method_decorator(xprez_staff_member_required)
    def add_item_view(cls, request, module_pk):
        module = cls.objects.get(pk=module_pk)
        item = module.create_item()
        form_class = module.get_admin_item_form_class(item)
        item.admin_form = form_class(instance=item, prefix=item.key)
        return HttpResponse(
            render_to_string(
                cls.admin_item_template_name,
                {"item": item, "module": module},
            )
        )

    @classmethod
    def get_add_item_url_name(cls):
        return "{}_ajax_add_item".format(cls.__name__.lower())

    @property
    def xprez_add_item_url_name(self):
        ns = getattr(self, "_xprez_admin_namespace", None)
        return "{}:{}".format(ns, self.get_add_item_url_name()) if ns else ""

    class Meta:
        abstract = True


class MultiModuleItem(models.Model):
    """
    Base class for items within MultiModule modules.
    Expected to add `module` as a FK to the MultiModule descendant.
    """

    module_foreign_key = "module"
    saved = models.BooleanField(default=False, editable=False)
    position = models.PositiveSmallIntegerField(default=0)

    @property
    def key(self):
        module_pk = getattr(self, f"{self.module_foreign_key}_id")
        return f"item-module-{module_pk}-{self.pk}"

    def copy(self, for_module, save=True):
        if not for_module:
            for_module = getattr(self, self.module_foreign_key)
        initial = {
            field.name: getattr(self, field.name)
            for field in self._meta.fields
            if not field.primary_key
        }
        inst = self.__class__(**initial)
        setattr(inst, self.module_foreign_key, for_module)
        if save:
            inst.save()
        return inst

    class Meta:
        abstract = True
        ordering = ("position",)


class UploadMultiModule(MultiModule):
    """Multi-module with AJAX file upload support."""

    admin_template_name = "xprez/admin/modules/multi_module/upload_multi_module.html"
    admin_js_controller_class = "XprezUploadMultiModule"

    class Meta:
        abstract = True

    def create_item_from_file(self, file):
        """Create item from uploaded file; saves to DB with saved=False."""
        item_model = getattr(self, self.items_attribute).model
        return item_model.create_from_file(file, self)

    @classmethod
    @method_decorator(xprez_staff_member_required)
    def upload_item_view(cls, request, module_pk):
        """Handle one file per request; returns HTML for the new item row."""
        module = cls.objects.get(pk=module_pk)
        file = request.FILES.get("file")
        if not file:
            return JsonResponse(status=400, data={"error": "No file uploaded"})
        item = module.create_item_from_file(file)
        form_class = module.get_admin_item_form_class(item)
        item.admin_form = form_class(instance=item, prefix=item.key)
        return HttpResponse(
            render_to_string(
                cls.admin_item_template_name,
                {"item": item, "module": module},
            )
        )

    @classmethod
    def get_admin_urls(cls):
        cls_name = cls.__name__.lower()
        return super().get_admin_urls() + [
            re_path(
                r"^{}/upload-item/(?P<module_pk>\d+)/".format(cls_name),
                cls.upload_item_view,
                name=cls.get_upload_url_name(),
            ),
        ]

    @classmethod
    def get_upload_url_name(cls):
        return "{}_ajax_upload_item".format(cls.__name__.lower())

    @property
    def xprez_upload_item_url_name(self):
        ns = getattr(self, "_xprez_admin_namespace", None)
        return "{}:{}".format(ns, self.get_upload_url_name()) if ns else ""
