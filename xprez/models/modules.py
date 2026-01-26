from django.apps import apps
from django.db import models
from django.db.models import F
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.urls import re_path
from django.utils.decorators import method_decorator
from django.utils.functional import classproperty

from xprez.admin.permissions import xprez_staff_member_required
from xprez.conf import settings
from xprez.models.configs import ConfigParentMixin
from xprez.utils import class_content_type, import_class

CLIPBOARD_TEXT_MAX_LENGTH = 100


class Module(ConfigParentMixin, models.Model):
    """Base module class for content blocks within sections."""

    config_model = "xprez.ModuleConfig"
    form_class = "xprez.admin.forms.BaseModuleForm"
    js_controller_class = "XprezModule"

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
        return f"xprez-{cls.module_key}"

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
        cls = import_class(self.form_class)
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
        self.admin_form.xprez_configs = self.get_configs()

        for config in self.admin_form.xprez_configs:
            config.build_admin_form(admin, data, files)

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
    def icon_template_name(cls):
        return [
            f"xprez/admin/icons/modules/{cls.module_key}.html",
            "xprez/admin/icons/modules/default.html",
        ]

    @classproperty
    def icon(cls):
        return render_to_string(cls.icon_template_name)

    def clipboard_verbose_name(self):
        return self.polymorph()._meta.verbose_name

    def clipboard_text_preview(self):
        return ""


class MultiModule(Module):
    """Module with multiple child items."""

    formset_factory = NotImplemented

    items_attribute = "items"

    def get_formset_queryset(self):
        return getattr(self, self.items_attribute).all()

    def build_admin_form(self, admin, data=None, files=None):
        super().build_admin_form(admin, data)
        FormSet = import_class(self.formset_factory)
        self.formset = FormSet(
            instance=self,
            queryset=self.get_formset_queryset(),
            data=data,
            files=files,
            prefix=f"{self.key}-items",
        )

    def save_admin_form(self, request):
        super().save_admin_form(request)
        self.formset.save()

    def is_admin_form_valid(self):
        return super().is_admin_form_valid() and self.formset.is_valid()

    def admin_has_errors(self):
        return super().admin_has_errors() or (
            self.formset.total_error_count() > 0 and not self.formset.is_valid()
        )

    def copy(self, for_container=None, save=True, position=None):
        inst = super().copy(for_container, save=save, position=position)
        if save:
            self.copy_items(inst)
        return inst

    def copy_items(self, inst):
        for item in self.get_formset_queryset():
            item.copy(inst)

    class Meta:
        abstract = True


class MultiModuleItem(models.Model):
    """
    Base class for items within MultiModule modules.
    Expected to add `module` as a FK to the MultiModule descendant.
    """

    module_foreign_key = "module"

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


class UploadMultiModule(MultiModule):
    """Multi-module with AJAX file upload support."""

    admin_formset_item_template_name = NotImplemented

    class Meta:
        abstract = True

    class AdminMedia:
        js = (
            "xprez/admin/libs/dropzone/dropzone.js",
            "xprez/admin/js/upload_multi_module.js",
        )

    @classmethod
    @method_decorator(xprez_staff_member_required)
    def upload_file_view(cls, request, module_pk):
        module = cls.objects.get(pk=module_pk)
        file_list = request.FILES.getlist("file")
        if len(file_list) > 0:
            file_ = file_list[0]
            FormSet = import_class(cls.formset_factory)
            item = FormSet.model.create_from_file(file_, module)
            queryset = module.get_formset_queryset()
            item_formset = FormSet(
                instance=module,
                queryset=queryset,
                prefix=f"module-{module.pk}-items",
            )
            item_form = item_formset.forms[-1]
            return JsonResponse(
                data={
                    "form": item_form.as_p(),
                    "template": render_to_string(
                        cls.admin_formset_item_template_name,
                        {
                            "item": item,
                            "module": module,
                            "number": queryset.count() - 1,
                        },
                    ),
                }
            )
        return JsonResponse(status=400, data={"error": "No files uploaded"})

    @classmethod
    def get_admin_urls(cls):
        cls_name = cls.__name__.lower()
        return [
            re_path(
                r"^{}/upload-item/(?P<module_pk>\d+)/".format(cls_name),
                cls.upload_file_view,
                name=cls.get_upload_url_name(),
            ),
        ]

    @classmethod
    def get_upload_url_name(self):
        return "{}_ajax_upload_item".format(self.__class__.__name__.lower())
