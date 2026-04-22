from django.db import models, transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import path
from django.utils.decorators import method_decorator

from xprez import constants
from xprez.admin.permissions import xprez_staff_member_required
from xprez.models.modules import Module
from xprez.utils import copy_model, import_class, resolve_saved


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
        else:
            return list(qs.all())

    def build_admin_form(self, admin, data=None, files=None):
        super().build_admin_form(admin, data, files)
        items = self.get_items_queryset(data)
        self.admin_form.xprez_items = []
        for item in items:
            form_class = self.get_admin_item_form_class(item)
            item.admin_form = form_class(
                instance=item, prefix=item.instance_key, data=data, files=files
            )
            self.admin_form.xprez_items += [item]
        if data:
            self.admin_form.xprez_items.sort(
                key=lambda item: item.admin_form.get_position()
            )

    def is_admin_form_valid(self):
        super_is_valid = super().is_admin_form_valid()
        if getattr(self.admin_form, "deleted", False):
            return True
        self.admin_form.xprez_items_all_valid = True
        for item in self.admin_form.xprez_items:
            if not item.is_admin_form_valid():
                self.admin_form.xprez_items_all_valid = False
        return super_is_valid and self.admin_form.xprez_items_all_valid

    @transaction.atomic
    def save_admin_form(self, request):
        super().save_admin_form(request)
        if not getattr(self.admin_form, "deleted", False):
            for item in self.admin_form.xprez_items:
                item.save_admin_form(request)

    def admin_has_errors(self):
        if getattr(self.admin_form, "deleted", False):
            return False
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

    @transaction.atomic
    def duplicate_to(self, target_section, saved=constants.SAVED_FORCE_FALSE, **kwargs):
        new_module = super().duplicate_to(target_section, saved=saved, **kwargs)
        self.duplicate_items(new_module, saved=saved)
        return new_module

    def duplicate_items(self, new_module, saved=constants.SAVED_FORCE_FALSE):
        for item in (
            getattr(self, self.items_attribute).all().order_by("position", "pk")
        ):
            item.duplicate_to(new_module, saved=saved)

    @classmethod
    def get_admin_urls(cls):
        cls_name = cls.__name__.lower()
        return [
            path(
                f"{cls_name}/add-item/<int:module_pk>/",
                cls.add_item_view,
                name=cls.get_add_item_url_name(),
            ),
        ]

    @classmethod
    @method_decorator(xprez_staff_member_required)
    def add_item_view(cls, request, module_pk):
        module = get_object_or_404(cls, pk=module_pk)
        item = module.create_item()
        form_class = module.get_admin_item_form_class(item)
        item.admin_form = form_class(instance=item, prefix=item.instance_key)
        html = render_to_string(
            cls.admin_item_template_name,
            {"item": item, "module": module},
        )
        return JsonResponse([{"html": html}], safe=False)

    @classmethod
    def get_add_item_url_name(cls):
        return f"{cls.__name__.lower()}_ajax_add_item"

    @property
    def xprez_add_item_url_name(self):
        ns = getattr(self, "_xprez_admin_namespace", None)
        return f"{ns}:{self.get_add_item_url_name()}" if ns else ""

    class Meta:
        abstract = True


class MultiModuleItem(models.Model):
    """
    Abstract base class for items within MultiModule modules.
    Expected to add `module` as a FK to the MultiModule descendant.
    """

    module_foreign_key = "module"
    saved = models.BooleanField(default=False, editable=False)
    position = models.PositiveSmallIntegerField(default=0, blank=True)

    @property
    def instance_key(self):
        module_pk = getattr(self, f"{self.module_foreign_key}_id")
        return f"item-module-{module_pk}-{self.pk}"

    def is_admin_form_valid(self):
        is_valid = self.admin_form.is_valid()
        if getattr(self.admin_form, "deleted", False):
            return True
        else:
            return is_valid

    def save_admin_form(self, request):
        if getattr(self.admin_form, "deleted", False):
            self.delete()
        elif self.admin_form.is_valid():
            inst = self.admin_form.save(commit=False)
            inst.position = self.admin_form.get_position()
            inst.saved = True
            inst.save()

    def duplicate_to(self, target_module, saved=constants.SAVED_FORCE_FALSE):
        new_item = copy_model(self)
        setattr(new_item, self.module_foreign_key, target_module)
        new_item.saved = resolve_saved(saved, self.saved)
        new_item.save()
        return new_item

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
        module = get_object_or_404(cls, pk=module_pk)
        file = request.FILES.get("file")
        if not file:
            return JsonResponse(status=400, data={"error": "No file uploaded"})
        item = module.create_item_from_file(file)
        form_class = module.get_admin_item_form_class(item)
        item.admin_form = form_class(instance=item, prefix=item.instance_key)
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
            path(
                f"{cls_name}/upload-item/<int:module_pk>/",
                cls.upload_item_view,
                name=cls.get_upload_url_name(),
            ),
        ]

    @classmethod
    def get_upload_url_name(cls):
        return f"{cls.__name__.lower()}_ajax_upload_item"

    @property
    def xprez_upload_item_url_name(self):
        ns = getattr(self, "_xprez_admin_namespace", None)
        return f"{ns}:{self.get_upload_url_name()}" if ns else ""
