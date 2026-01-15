from django.db import models

from xprez.conf import settings
from xprez.models.modules import Module


class ModuleSymlink(Module):
    admin_template_name = "xprez/admin/modules/module_symlink.html"
    icon_template_name = "xprez/admin/icons/modules/module_symlink.html"
    symlink = models.ForeignKey(
        Module,
        on_delete=models.SET_NULL,
        null=True,
        editable=False,
        related_name="symlinked_module_set",
    )

    class Meta:
        verbose_name = "Linked module"

    def render_front(self, *args, **kwargs):
        if self.symlink:
            return self.symlink.polymorph().render_front(*args, **kwargs)
        else:
            return ""


class SectionSymlink(Module):
    admin_template_name = "xprez/admin/modules/section_symlink.html"
    icon_template_name = "xprez/admin/icons/modules/section_symlink.html"
    symlink = models.ForeignKey(
        settings.XPREZ_SECTION_MODEL_CLASS,
        on_delete=models.SET_NULL,
        null=True,
        editable=False,
        related_name="symlinked_section_set",
    )

    class Meta:
        verbose_name = "Linked section"

    def render_front(self, context):
        if self.symlink:
            return self.symlink.render_front(context)
        else:
            return ""
