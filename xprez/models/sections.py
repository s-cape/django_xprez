from django.db import models
from django.template.defaultfilters import pluralize
from django.template.loader import render_to_string
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from xprez import constants
from xprez.conf import defaults, settings
from xprez.models.configs import ConfigParentMixin
from xprez.models.mixins.cache import ContentFrontCacheMixin, FrontCacheMixin
from xprez.utils import import_class


class SectionBase(models.Model):
    front_cacheable = False
    container = models.ForeignKey(
        "xprez.Container",
        on_delete=models.SET_NULL,
        related_name="%(class)ss",
        editable=False,
        null=True,
    )
    position = models.PositiveSmallIntegerField(default=0, blank=True)
    visible = models.BooleanField(default=True)
    saved = models.BooleanField(default=False, editable=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    changed = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True
        ordering = ("position",)

    @property
    def instance_key(self):
        return f"{self._meta.model_name}-{self.pk}"

    def render_front(self, context):
        raise NotImplementedError

    def render_admin(self, context):
        context[
            "available_modules"
        ] = self.admin_form.xprez_admin.xprez_add_menu_module_classes(self.container)
        return render_to_string(self.admin_template_name, context)

    def build_admin_form(self, admin, data=None, files=None):
        raise NotImplementedError

    def is_admin_form_valid(self):
        return self.admin_form.is_valid()

    def save_admin_form(self, request):
        inst = self.admin_form.save(commit=False)
        inst.saved = True
        inst.save()

    def duplicate_to(self, target_container, saved=False):
        raise NotImplementedError


class Section(ContentFrontCacheMixin, ConfigParentMixin, SectionBase):
    KEY = constants.SECTION_KEY
    front_template_name = "xprez/section.html"
    admin_template_name = "xprez/admin/sections/section.html"

    max_width_choice = models.CharField(
        verbose_name=_("Max width"),
        max_length=16,
        choices=constants.MAX_WIDTH_CHOICES,
        default=defaults.XPREZ_DEFAULTS["section"]["max_width_choice"],
    )
    max_width_custom = models.PositiveIntegerField(
        null=True,
        blank=True,
        default=defaults.XPREZ_DEFAULTS["section"]["max_width_custom"],
    )
    alternate_background = models.BooleanField(
        default=defaults.XPREZ_DEFAULTS["section"]["alternate_background"]
    )
    background_color = models.CharField(
        max_length=30,
        blank=True,
        default=defaults.XPREZ_DEFAULTS["section"]["background_color"],
    )
    css_class = models.CharField(max_length=100, null=True, blank=True)

    @property
    def instance_key(self):
        return f"{self.KEY}-{self.pk}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.pk:
            self.get_or_create_config(0)

    def invalidate_front_cache(self):
        super().invalidate_front_cache()
        if self.container_id:
            self.container.invalidate_front_cache()
        for symlinked in self.symlinked_section_set.filter(saved=True):
            symlinked.invalidate_front_cache()

    @cached_property
    def front_cacheable(self):
        return all(m.polymorph.front_cacheable for m in self.get_modules_front())

    def build_config(self, css_breakpoint):
        return self.configs.model(
            section=self,
            css_breakpoint=css_breakpoint,
            **settings.XPREZ_DEFAULTS["section_config"],
        )

    def get_css_config_keys(self):
        return ("section",)

    def get_css_classes(self):
        classes = {"section": True}
        if self.alternate_background:
            classes["alternate-background"] = True
        return classes

    def get_css_variables(self):
        css_variables = {
            "max-width": self._get_choice_or_custom("max_width"),
        }
        if self.background_color:
            css_variables["section-background-color"] = self.background_color
        return css_variables

    def build_admin_form(self, admin, data=None, files=None):
        form_class = import_class("xprez.admin.forms.SectionForm")
        self.admin_form = form_class(
            instance=self, prefix=self.instance_key, data=data, files=files
        )
        self.admin_form.xprez_admin = admin
        self.admin_form.xprez_modules_all_valid = None
        self.admin_form.xprez_modules = self.modules.all().polymorphs()

        for module in self.admin_form.xprez_modules:
            module.build_admin_form(admin, data, files)

        if data:
            self.admin_form.xprez_modules.sort(
                key=lambda m: m.admin_form.get_position()
            )

        self.admin_form.xprez_configs_all_valid = None
        if data:
            ids = [int(id) for id in data.getlist("section-config-id")]
            self.admin_form.xprez_configs = list(
                self.configs.filter(pk__in=ids).order_by("css_breakpoint")
            )
        else:
            self.admin_form.xprez_configs = list(self.get_configs().filter(saved=True))

        for config in self.admin_form.xprez_configs:
            config.build_admin_form(admin, data, files)

    def is_admin_form_valid(self):
        super_is_valid = super().is_admin_form_valid()
        if getattr(self.admin_form, "deleted", False):
            return True
        self.admin_form.xprez_modules_all_valid = True
        for module in self.admin_form.xprez_modules:
            if not module.is_admin_form_valid():
                self.admin_form.xprez_modules_all_valid = False

        self.admin_form.xprez_configs_all_valid = True
        for config in self.admin_form.xprez_configs:
            if not config.is_admin_form_valid():
                self.admin_form.xprez_configs_all_valid = False

        return (
            super_is_valid
            and self.admin_form.xprez_modules_all_valid
            and self.admin_form.xprez_configs_all_valid
        )

    def save_admin_form(self, request):
        super().save_admin_form(request)
        for module in self.admin_form.xprez_modules:
            module.save_admin_form(request)

        for config in self.admin_form.xprez_configs:
            config.save_admin_form(request)
        self._prune_redundant_configs()

    def render_admin(self, context):
        context["section"] = self
        return super().render_admin(context)

    def get_modules_front(self):
        if not hasattr(self, "_modules_front"):
            self._modules_front = self.modules.filter(saved=True).polymorphs()
        return self._modules_front

    def duplicate_to(self, target_container, saved=False):
        new_section = self.__class__.objects.create(
            container=target_container, saved=saved
        )
        self.duplicate_configs_to(new_section, saved=saved)
        for module in self.modules.filter(saved=True).polymorphs():
            module.duplicate_to(new_section, saved=saved)
        return new_section

    def clipboard_verbose_name(self):
        return self._meta.verbose_name

    def clipboard_text_preview(self):
        count = self.modules.filter(saved=True).count()
        return f"{count} module{pluralize(count)}"

    def render_front(self, context):
        context["section"] = self
        return render_to_string(self.front_template_name, context)


class SectionSymlink(FrontCacheMixin, SectionBase):
    KEY = constants.SECTION_SYMLINK_KEY
    front_cacheable = False
    admin_template_name = "xprez/admin/sections/section_symlink.html"

    symlink = models.ForeignKey(
        "xprez.Section",
        on_delete=models.SET_NULL,
        null=True,
        editable=False,
        related_name="symlinked_section_set",
    )

    class Meta:
        verbose_name = _("Linked section")

    def invalidate_front_cache(self):
        super().invalidate_front_cache()
        if self.container_id:
            self.container.invalidate_front_cache()

    def build_admin_form(self, admin, data=None, files=None):
        form_class = import_class("xprez.admin.forms.SectionSymlinkForm")
        self.admin_form = form_class(
            instance=self, prefix=self.instance_key, data=data, files=files
        )
        self.admin_form.xprez_admin = admin

    def render_admin(self, context):
        context["section_symlink"] = self
        return super().render_admin(context)

    def duplicate_to(self, target_container, saved=False):
        return SectionSymlink.objects.create(
            container=target_container, symlink=self.symlink, saved=saved
        )

    def render_front(self, context):
        if self.symlink:
            return self.symlink.render_front_cached(context)
        else:
            return ""

    def render_front_cached(self, context):
        if self.symlink:
            return self.symlink.render_front_cached(context)
        else:
            return ""
