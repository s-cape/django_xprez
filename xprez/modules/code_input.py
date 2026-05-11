from django.db import models
from django.utils.translation import gettext_lazy as _

from xprez import constants
from xprez.admin.forms import ModuleForm
from xprez.models.modules import Module
from xprez.utils import truncate_with_ellipsis


class CodeInputModule(Module):
    front_cacheable = False
    front_template_name = "xprez/modules/code_input.html"
    admin_template_name = "xprez/admin/modules/code_input.html"
    admin_form_class = "xprez.modules.code_input.CodeInputModuleForm"
    admin_icon_template_name = "xprez/shared/icons/modules/code_input.html"

    code = models.TextField()

    class Meta:
        verbose_name = _("Code Input")

    def show_front(self):
        return self.code

    def preview_text(self):
        if not self.code or not self.code.strip():
            return None
        lines = [line.strip() for line in self.code.splitlines() if line.strip()]
        if not lines:
            return None
        snippet = " ".join(lines)
        return truncate_with_ellipsis(snippet, constants.PREVIEW_TEXT_MAX_LENGTH)


class CodeInputModuleForm(ModuleForm):
    class Meta:
        model = CodeInputModule
        fields = "__all__"
