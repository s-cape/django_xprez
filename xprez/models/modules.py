from django.apps import apps
from django.db import models
from django.db.models import F
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.urls import re_path
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property, classproperty

from xprez import constants
from xprez.admin.permissions import xprez_staff_member_required
from xprez.conf import defaults, settings
from xprez.models.configs import ConfigParentMixin
from xprez.utils import class_content_type, import_class

CLIPBOARD_TEXT_MAX_LENGTH = 100


class Module(ConfigParentMixin, models.Model):
    """Base module class for content blocks within sections."""

    constants = constants

    config_model = "xprez.ModuleConfig"
    admin_form_class = "xprez.admin.forms.ModuleForm"
    admin_js_controller_class = "XprezModule"

    # SIZE_FULL = "full"
    # SIZE_MID = "mid"
    # SIZE_TEXT = "text"
    # SIZE_CHOICES = (
    #     (SIZE_FULL, "full"),
    #     (SIZE_MID, "mid"),
    #     (SIZE_TEXT, "text"),
    # )

    section = models.ForeignKey(
        settings.XPREZ_SECTION_MODEL_CLASS,
        on_delete=models.CASCADE,
        related_name="modules",
    )
    saved = models.BooleanField(default=False, editable=False)

    position = models.PositiveSmallIntegerField(default=0)
    content_type = models.CharField(max_length=100, editable=False)
    css_class = models.CharField(max_length=100, null=True, blank=True)
    alternate_color = models.BooleanField(
        default=defaults.XPREZ_DEFAULTS["module"]["default"]["alternate_color"]
    )

    created = models.DateTimeField(auto_now_add=True, editable=False, db_index=True)
    changed = models.DateTimeField(auto_now=True, editable=False, db_index=True)

    class Meta:
        ordering = ("position",)

    class AdminMedia:
        js = []
        css = {}

    class FrontMedia:
        js = []
        css = {}

    def __str__(self):
        return self.content_type

    def save(self, *args, **kwargs):
        if not self.pk:
            self.content_type = self.class_content_type()
        super().save(*args, **kwargs)
        if self.pk:
            self.get_or_create_config(settings.XPREZ_DEFAULT_BREAKPOINT)

    @property
    def verbose_name(self):
        return self._meta.verbose_name.title()

    @classmethod
    def class_content_type(cls):
        return class_content_type(cls)

    @classproperty
    def module_key(cls):
        return cls._meta.model_name.lower().removesuffix("module")

    @classmethod
    def module_css_class(cls):
        return cls.module_key

    @property
    def key(self):
        return f"module-{self.pk}"

    @property
    def admin_template_name(self):
        return [
            f"xprez/admin/modules/{self.module_key}.html",
            "xprez/admin/modules/base.html",
        ]

    @property
    def front_template_name(self):
        return f"xprez/modules/{self.module_key}.html"

    @cached_property
    def polymorph(self):
        app_label, object_name = self.content_type.split(".")
        model = apps.get_model(app_label, object_name)
        if isinstance(self, model):
            return self
        else:
            return model.objects.get(pk=self.pk)

    def copy(self, for_container=None, save=True, position=None):
        if not for_container:
            for_container = self.container

        initial = {
            field.name: getattr(self, field.name)
            for field in self._meta.fields
            if not field.primary_key
        }
        inst = self.__class__(**initial)
        if position is None:
            inst.position = self._count_new_module_position(for_container)
        else:
            inst.position = position
            if for_container.modules.filter(position=position).exists():
                for_container.modules.filter(position__gte=position).update(
                    position=F("position") + 1
                )
        inst.container = for_container
        if save:
            inst.save()
        return inst

    def get_config_model(self):
        app_label, model_name = self.config_model.split(".")
        return apps.get_model(app_label, model_name)

    def get_configs(self):
        return (
            self.get_config_model()
            .objects.filter(module=self)
            .order_by("css_breakpoint")
        )

    def get_saved_configs(self):
        return self.get_configs().filter(saved=True)

    @classmethod
    def build(cls):
        content_type = cls.class_content_type()
        module_defaults = {"content_type": content_type}
        module_defaults.update(settings.XPREZ_DEFAULTS["module"].get("default", {}))
        module_defaults.update(settings.XPREZ_DEFAULTS["module"].get(content_type, {}))
        return cls(**module_defaults)

    def build_config(self, css_breakpoint):
        config_model = self.get_config_model()
        config_defaults = (
            settings.XPREZ_DEFAULTS["module_config"].get("default", {}).copy()
        )
        config_defaults.update(
            settings.XPREZ_DEFAULTS["module_config"].get(self.class_content_type(), {})
        )
        return config_model(
            module=self,
            css_breakpoint=css_breakpoint,
            **config_defaults,
        )

    def get_admin_form_class(self):
        cls = import_class(self.admin_form_class)
        if cls._meta.model:
            return cls
        else:

            class ModuleForm(cls):
                class Meta(cls.Meta):
                    model = self.__class__

            return ModuleForm

    def build_admin_form(self, admin, data=None, files=None):
        form_class = self.get_admin_form_class()
        self.admin_form = form_class(
            instance=self, prefix=self.key, data=data, files=files
        )
        self.admin_form.xprez_admin = admin

        self.admin_form.xprez_configs_all_valid = None
        if data:
            ids = [int(id) for id in data.getlist("module-config-id")]
            self.admin_form.xprez_configs = list(
                self.get_config_model()
                .objects.filter(module=self, pk__in=ids)
                .order_by("css_breakpoint")
            )
        else:
            self.admin_form.xprez_configs = list(self.get_saved_configs())

        for config in self.admin_form.xprez_configs:
            config.build_admin_form(admin, data, files)
        if getattr(admin, "admin_site", None):
            self._xprez_admin_namespace = admin.admin_site.name

    def is_admin_form_valid(self):
        self.admin_form.xprez_configs_all_valid = True
        for config in self.admin_form.xprez_configs:
            if not config.is_admin_form_valid():
                self.admin_form.xprez_configs_all_valid = False

        return self.admin_form.is_valid() and self.admin_form.xprez_configs_all_valid

    def save_admin_form(self, request):
        inst = self.admin_form.save(commit=False)
        inst.saved = True
        inst.save()

        for config in self.admin_form.xprez_configs:
            if config.admin_form.cleaned_data.get("delete"):
                config.delete()
            else:
                config.saved = True
                config.save_admin_form(request)

    def render_admin(self, context):
        xprez_admin = self.admin_form.xprez_admin
        context.update(
            {
                "module": self,
                "xprez_admin": xprez_admin,
            }
        )
        return render_to_string(self.admin_template_name, context)

    def render_front(self, context):
        context["module"] = self
        return render_to_string(self.front_template_name, context)

    def admin_has_errors(self):
        return bool(self.admin_form.errors)

    @classmethod
    def get_admin_urls(cls):
        return []

    @classproperty
    def admin_icon_template_name(cls):
        return [
            f"xprez/admin/icons/modules/{cls.module_key}.html",
            "xprez/admin/icons/modules/default.html",
        ]

    @classproperty
    def admin_icon(cls):
        return render_to_string(cls.admin_icon_template_name)

    def clipboard_verbose_name(self):
        return self.polymorph._meta.verbose_name

    def clipboard_text_preview(self):
        return ""

    def get_css_config_keys(self):
        return ("module",)

    def get_css_classes(self):
        classes = {
            "module": True,
            self.module_css_class(): True,
        }
        if self.alternate_color:
            classes["alternate-color"] = True
        return classes


class FontSizeModuleMixin(models.Model):
    """Mixin that adds font_size field to modules."""

    font_size = models.CharField(
        "Font size",
        max_length=20,
        choices=constants.FONT_SIZE_CHOICES,
        default=constants.FONT_SIZE_NORMAL,
    )

    def get_css_classes(self):
        classes = super().get_css_classes()
        if self.font_size != constants.FONT_SIZE_UNSET:
            classes["font-size"] = self.font_size
        return classes

    class Meta:
        abstract = True


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

    def get_items_queryset(self, data=None):
        qs = getattr(self, self.items_attribute)
        if data is None:
            return qs.filter(saved=True).order_by("position")
        ids = [int(id) for id in data.getlist("item-id")]
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
        """Build an unsaved item instance (no DB save)."""
        item_model = getattr(self, self.items_attribute).model
        position = getattr(self, self.items_attribute).count()
        return item_model(**{item_model.module_foreign_key: self, "position": position})

    def create_item(self):
        """Build + save item with saved=False."""
        item = self.build_item()
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
        return f"item-{self.pk}"

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
