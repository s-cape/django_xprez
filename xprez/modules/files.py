from django.db import models
from django.utils.translation import gettext_lazy as _

from xprez.admin.forms import ModuleForm
from xprez.models.mixins.font_size import FontSizeModuleMixin
from xprez.models.multi_module import MultiModuleItem, UploadMultiModule


class FilesModule(FontSizeModuleMixin, UploadMultiModule):
    front_template_name = "xprez/modules/files.html"
    admin_template_name = "xprez/admin/modules/files/files.html"
    admin_item_template_name = "xprez/admin/modules/files/files_item.html"
    admin_form_class = "xprez.modules.files.FilesModuleForm"
    admin_icon_template_name = "xprez/shared/icons/modules/files.html"

    title = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = _("Files")


class FilesItem(MultiModuleItem):
    module = models.ForeignKey(
        FilesModule,
        related_name="items",
        on_delete=models.CASCADE,
        editable=False,
    )
    file = models.FileField(upload_to="files", max_length=300)
    description = models.CharField(max_length=255, blank=True)

    def get_description(self):
        return self.description or self.get_file_stem()

    def get_file_name(self):
        try:
            return self.file.name.split("/")[-1]
        except (IndexError, AttributeError):
            return ""

    def get_file_extension(self):
        name = self.get_file_name()
        if "." in name:
            return name.rsplit(".", 1)[-1].lower()
        else:
            return ""

    def get_file_stem(self):
        name = self.get_file_name()
        if name:
            return name.rsplit(".", 1)[0]
        else:
            return ""

    @classmethod
    def create_from_file(cls, django_file, module):
        item = cls(module=module, position=module.items.count())
        item.file.save(django_file.name.split("/")[-1], django_file)
        item.save()
        return item


class FilesModuleForm(ModuleForm):
    options_fields = ModuleForm.options_fields + ("font_size",)
