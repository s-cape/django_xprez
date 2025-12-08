from django.db import models
from django.template.loader import render_to_string

from xprez.conf import settings
from xprez.utils import import_class


class Section(models.Model):
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

    MAX_WIDTH_SMALL = "small"
    MAX_WIDTH_MEDIUM = "medium"
    MAX_WIDTH_FULL = "full"
    MAX_WIDTH_CUSTOM = "custom"
    MAX_WIDTH_CHOICES = (
        (MAX_WIDTH_SMALL, "Small"),
        (MAX_WIDTH_MEDIUM, "Medium"),
        (MAX_WIDTH_FULL, "Full"),
        (MAX_WIDTH_CUSTOM, "Custom"),
    )
    max_width_choice = models.CharField(
        verbose_name="Max width",
        max_length=16,
        choices=MAX_WIDTH_CHOICES,
        default=MAX_WIDTH_FULL,
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
            for css_breakpoint in settings.XPREZ_BREAKPOINTS.keys():
                self.configs.get_or_create(css_breakpoint=css_breakpoint)

    def get_form_prefix(self):
        return "section-" + str(self.pk)

    def build_admin_form(self, admin, data=None, files=None):
        form_class = import_class("xprez.admin.forms.SectionForm")
        self.admin_form = form_class(
            instance=self, prefix=self.get_form_prefix(), data=data, files=files
        )
        self.admin_form.xprez_admin = admin
        self.admin_form.xprez_contents_all_valid = None
        self.admin_form.xprez_contents = [c.polymorph() for c in self.contents.all()]

        for content in self.admin_form.xprez_contents:
            content.build_admin_form(admin, data, files)

        self.admin_form.xprez_configs_all_valid = None
        self.admin_form.xprez_configs = self.get_configs()

        for config in self.admin_form.xprez_configs:
            config.build_admin_form(admin, data, files)

        # self.admin_form.xprez_contents = sorted(
        #     self.admin_form.xprez_contents,
        #     key=lambda content: int(content.admin_form["position"].value() or 0),
        # )

    def is_admin_form_valid(self):
        self.admin_form.xprez_contents_all_valid = True
        for content in self.admin_form.xprez_contents:
            if not content.is_admin_form_valid():
                self.admin_form.xprez_contents_all_valid = False

        self.admin_form.xprez_configs_all_valid = True
        for config in self.admin_form.xprez_configs:
            if not config.is_admin_form_valid():
                self.admin_form.xprez_configs_all_valid = False

        return (
            self.admin_form.is_valid()
            and self.admin_form.xprez_contents_all_valid
            and self.admin_form.xprez_configs_all_valid
        )

    def save_admin_form(self, request):
        inst = self.admin_form.save(commit=False)
        inst.save()
        for content in self.admin_form.xprez_contents:
            if content.admin_form.cleaned_data.get("delete"):
                content.delete()
            else:
                content.save_admin_form(request)

        for config in self.admin_form.xprez_configs:
            config.save_admin_form(request)

    def render_admin(self, context):
        # xprez_admin = self.admin_form.xprez_admin
        # form = self.admin_form
        context.update(
            {
                "section": self,
                # "form": form,
                # "xprez_admin": xprez_admin,
                "allowed_contents": self.admin_form.xprez_admin.xprez_get_allowed_contents(
                    container=self.container
                ),
            }
        )
        return render_to_string(self.admin_template_name, context)

    def get_contents(self):
        if not hasattr(self, "_contents"):
            self._contents = self.contents.filter(saved=True)
            # self._contents = self.contents.all()  # TODO: filter(saved=True)
        return self._contents

    def get_configs(self):
        if not hasattr(self, "_configs"):
            self._configs = self.configs.filter(visible=True)
        return self._configs

    def render_front(self, context):
        context["section"] = self
        return render_to_string(self.front_template_name, context)
