from django.apps import apps
from django.db import models
from django.template.loader import render_to_string
from django.utils.functional import cached_property, classproperty

from xprez import constants
from xprez.conf import defaults, settings
from xprez.models.configs import ConfigParentMixin
from xprez.models.mixins.cache import ContentFrontCacheMixin
from xprez.models.querysets.modules import ModuleQuerySet
from xprez.utils import class_content_type, copy_model, import_class


class Module(ContentFrontCacheMixin, ConfigParentMixin, models.Model):
    """Base module class for content blocks within sections."""

    KEY = constants.MODULE_KEY
    constants = constants

    config_model = "xprez.ModuleConfig"
    admin_form_class = "xprez.admin.forms.ModuleForm"
    admin_js_controller_class = "XprezModule"

    section = models.ForeignKey(
        "xprez.Section",
        on_delete=models.CASCADE,
        related_name="modules",
    )
    saved = models.BooleanField(default=False, editable=False)

    position = models.PositiveSmallIntegerField(default=0, blank=True)
    content_type = models.CharField(max_length=100, editable=False)
    css_class = models.CharField(max_length=100, null=True, blank=True)
    alternate_color = models.BooleanField(
        default=defaults.XPREZ_DEFAULTS["module"]["default"]["alternate_color"]
    )

    live_sync = models.BooleanField("Change style for selected modules", default=True)
    sync_group = models.PositiveIntegerField(null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True, editable=False)
    changed = models.DateTimeField(auto_now=True, editable=False)

    objects = ModuleQuerySet.as_manager()

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
            self.get_or_create_config(0)

    def invalidate_front_cache(self):
        super().invalidate_front_cache()
        self.section.invalidate_front_cache()
        if self.section.container_id:
            self.section.container.invalidate_front_cache()
        module_symlink_model = apps.get_model("xprez", "ModuleSymlink")
        if not isinstance(self, module_symlink_model):
            for symlinked in self.symlinked_module_set.filter(saved=True):
                symlinked.invalidate_front_cache()

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
    def instance_key(self):
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

    def duplicate_to(self, target_section, saved=False, **kwargs):
        new_module = copy_model(self)
        new_module.section = target_section
        new_module.saved = saved
        new_module.save(**kwargs)
        self.duplicate_configs_to(new_module, saved=saved)
        return new_module

    def get_config_model(self):
        app_label, model_name = self.config_model.split(".")
        return apps.get_model(app_label, model_name)

    def get_configs(self):
        return (
            self.get_config_model()
            .objects.filter(module=self)
            .order_by("css_breakpoint")
        )

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
            instance=self, prefix=self.instance_key, data=data, files=files
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
            self.admin_form.xprez_configs = list(self.get_configs().filter(saved=True))

        for config in self.admin_form.xprez_configs:
            config.build_admin_form(admin, data, files)
        if getattr(admin, "xprez_url_namespace", None):
            self._xprez_admin_namespace = admin.xprez_url_namespace

    def is_admin_form_valid(self):
        is_valid = self.admin_form.is_valid()
        if getattr(self.admin_form, "deleted", False):
            return True
        self.admin_form.xprez_configs_all_valid = True
        for config in self.admin_form.xprez_configs:
            if not config.is_admin_form_valid():
                self.admin_form.xprez_configs_all_valid = False

        return is_valid and self.admin_form.xprez_configs_all_valid

    def save_admin_form(self, request):
        if getattr(self.admin_form, "deleted", False):
            self.delete()
        elif self.admin_form.is_valid():
            inst = self.admin_form.save(commit=False)
            inst.saved = True
            inst.save()

            for config in self.admin_form.xprez_configs:
                config.save_admin_form(request)
            self._prune_redundant_configs()

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
            f"xprez/shared/icons/modules/{cls.module_key}.html",
            "xprez/shared/icons/modules/default.html",
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
