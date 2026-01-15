from django.db import models
from django.template import TemplateDoesNotExist
from django.template.loader import get_template

from xprez.admin.fields import TemplatePathField
from xprez.admin.forms import BaseModuleForm
from xprez.conf import settings
from xprez.models.modules import Module


class CodeTemplateModule(Module):
    admin_template_name = "xprez/admin/modules/code_template.html"
    icon_template_name = "xprez/admin/icons/modules/code_template.html"
    form_class = "xprez.modules.code_template.CodeTemplateModuleForm"

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

    def render_front(self, context):
        if self.template_name:
            context["module"] = self
            try:
                return get_template(self.template_name).render(context=context)
            except TemplateDoesNotExist:
                return "Invalid Template"
        else:
            return ""


class CodeTemplateModuleForm(BaseModuleForm):
    class Meta:
        model = CodeTemplateModule
        fields = "__all__"
