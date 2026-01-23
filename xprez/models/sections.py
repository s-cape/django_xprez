from django.db import models
from django.template.loader import render_to_string

from xprez import constants
from xprez.conf import settings
from xprez.models.configs import ConfigParentMixin
from xprez.utils import import_class


class Section(ConfigParentMixin, models.Model):
    front_template_name = "xprez/section.html"
    admin_template_name = "xprez/admin/section.html"

    container = models.ForeignKey(
        settings.XPREZ_CONTAINER_MODEL_CLASS,
        on_delete=models.SET_NULL,
        related_name="sections",
        editable=False,
        null=True,
    )
    position = models.PositiveSmallIntegerField(default=0)
    visible = models.BooleanField(default=True)
    saved = models.BooleanField(default=False, editable=False)
    created = models.DateTimeField(auto_now_add=True, editable=False, db_index=True)
    changed = models.DateTimeField(auto_now=True, editable=False, db_index=True)

    max_width_choice = models.CharField(
        verbose_name="Max width",
        max_length=16,
        choices=constants.MAX_WIDTH_CHOICES,
        default=constants.MAX_WIDTH_FULL,
    )
    max_width_custom = models.PositiveIntegerField(null=True, blank=True)

    alternate_color = models.BooleanField(default=False)
    background_color = models.CharField(max_length=30, blank=True)
    css_class = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        ordering = ("position",)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.pk:
            self.get_or_create_config(settings.XPREZ_DEFAULT_BREAKPOINT)

    def build_config(self, css_breakpoint):
        return self.configs.model(
            section=self,
            css_breakpoint=css_breakpoint,
            **settings.XPREZ_SECTION_CONFIG_DEFAULTS,
        )

    @property
    def key(self):
        return f"section-{self.pk}"

    def build_admin_form(self, admin, data=None, files=None):
        form_class = import_class("xprez.admin.forms.SectionForm")
        self.admin_form = form_class(
            instance=self, prefix=self.key, data=data, files=files
        )
        self.admin_form.xprez_admin = admin
        self.admin_form.xprez_modules_all_valid = None
        self.admin_form.xprez_modules = [m.polymorph() for m in self.modules.all()]

        for module in self.admin_form.xprez_modules:
            module.build_admin_form(admin, data, files)

        if data:
            self.admin_form.xprez_modules.sort(
                key=lambda m: m.admin_form.get_position()
            )

        self.admin_form.xprez_configs_all_valid = None
        self.admin_form.xprez_configs = self.get_configs()

        for config in self.admin_form.xprez_configs:
            config.build_admin_form(admin, data, files)

    def is_admin_form_valid(self):
        self.admin_form.xprez_modules_all_valid = True
        for module in self.admin_form.xprez_modules:
            if not module.is_admin_form_valid():
                self.admin_form.xprez_modules_all_valid = False

        self.admin_form.xprez_configs_all_valid = True
        for config in self.admin_form.xprez_configs:
            if not config.is_admin_form_valid():
                self.admin_form.xprez_configs_all_valid = False

        return (
            self.admin_form.is_valid()
            and self.admin_form.xprez_modules_all_valid
            and self.admin_form.xprez_configs_all_valid
        )

    def save_admin_form(self, request):
        inst = self.admin_form.save(commit=False)
        inst.save()
        for module in self.admin_form.xprez_modules:
            if module.admin_form.cleaned_data.get("delete"):
                module.delete()
            else:
                module.save_admin_form(request)

        for config in self.admin_form.xprez_configs:
            if config.admin_form.cleaned_data.get("delete"):
                config.delete()
            else:
                config.save_admin_form(request)

    def render_admin(self, context):
        xprez_admin = self.admin_form.xprez_admin
        context.update(
            {
                "section": self,
                "available_modules": xprez_admin.xprez_get_available_modules(
                    container=self.container
                ),
            }
        )
        return render_to_string(self.admin_template_name, context)

    def get_modules(self):
        if not hasattr(self, "_modules"):
            self._modules = list(self.modules.filter(saved=True))
        return self._modules

    def render_front(self, context):
        context["section"] = self
        return render_to_string(self.front_template_name, context)
