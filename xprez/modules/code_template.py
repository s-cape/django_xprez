from django.db import models
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.utils.translation import gettext_lazy as _

from xprez.admin.fields import TemplatePathField
from xprez.admin.forms import ModuleForm
from xprez.conf import settings
from xprez.models.mixins.font_size import FontSizeModuleMixin
from xprez.models.modules import Module


class CodeTemplateModule(FontSizeModuleMixin, Module):
    admin_form_class = "xprez.modules.code_template.CodeTemplateModuleForm"
    admin_template_name = "xprez/admin/modules/code_template.html"
    admin_icon_template_name = "xprez/shared/icons/modules/code_template.html"

    @staticmethod
    def get_template_dir():
        if settings.XPREZ_CODE_TEMPLATES_DIR:
            return settings.XPREZ_CODE_TEMPLATES_DIR

        for engine in settings.TEMPLATES:
            if engine.get("DIRS"):
                return engine["DIRS"][0]

        return ""

    template_name = TemplatePathField(
        template_dir=get_template_dir(),
        prefix=settings.XPREZ_CODE_TEMPLATES_PREFIX,
        match=r"^(?!\.).+",
        max_length=255,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("Code Template")

    def preview_text(self):
        return self.template_name

    def render_front(self, context):
        if self.template_name:
            context["module"] = self
            try:
                return get_template(self.template_name).render(context=context)
            except TemplateDoesNotExist:
                return "Invalid Template"
        else:
            return ""


class CodeTemplateModuleForm(ModuleForm):
    options_fields = ModuleForm.options_fields + ("font_size",)

    class Meta:
        model = CodeTemplateModule
        fields = "__all__"
