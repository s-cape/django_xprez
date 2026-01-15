from django.db import models

from xprez.admin.forms import BaseModuleForm
from xprez.models.modules import Module


class CodeInputModule(Module):
    admin_template_name = "xprez/admin/modules/code_input.html"
    front_template_name = "xprez/modules/code_input.html"
    icon_template_name = "xprez/admin/icons/modules/code_input.html"
    form_class = "xprez.modules.code_input.CodeInputModuleForm"

    code = models.TextField()

    def show_front(self):
        return self.code


class CodeInputModuleForm(BaseModuleForm):
    class Meta:
        model = CodeInputModule
        fields = ("code",) + BaseModuleForm.base_module_fields
