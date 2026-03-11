from django.db import models
from django.utils.translation import gettext_lazy as _

from xprez.models.modules import Module


class ModuleSymlink(Module):
    admin_template_name = "xprez/admin/modules/module_symlink.html"
    admin_icon_template_name = "xprez/shared/icons/modules/module_symlink.html"
    symlink = models.ForeignKey(
        Module,
        on_delete=models.SET_NULL,
        null=True,
        editable=False,
        related_name="symlinked_module_set",
    )

    class Meta:
        verbose_name = _("Linked module")

    @property
    def front_cacheable(self):
        if self.symlink:
            return self.symlink.polymorph.front_cacheable
        else:
            return False

    def render_front(self, *args, **kwargs):
        if self.symlink:
            return self.symlink.polymorph.render_front(*args, **kwargs)
        else:
            return ""

    def render_front_cached(self, *args, **kwargs):
        if self.symlink:
            return self.symlink.polymorph.render_front_cached(*args, **kwargs)
        else:
            return ""

    def preview_text(self):
        if self.symlink:
            return self.symlink.polymorph.preview_text()
