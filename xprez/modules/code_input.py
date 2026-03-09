from django.db import models
from django.utils.translation import gettext_lazy as _

from xprez.admin.forms import ModuleForm
from xprez.models.modules import Module


class CodeInputModule(Module):
    front_template_name = "xprez/modules/code_input.html"
    admin_template_name = "xprez/admin/modules/code_input.html"
    admin_form_class = "xprez.modules.code_input.CodeInputModuleForm"
    admin_icon_template_name = "xprez/shared/icons/modules/code_input.html"

    code = models.TextField()

    class Meta:
        verbose_name = _("Code Input")

    def show_front(self):
        return self.code


class CodeInputModuleForm(ModuleForm):
    class Meta:
        model = CodeInputModule
        fields = "__all__"
