from django import forms
from django.db import models

from xprez.admin.forms import ModuleForm, MultiModuleItemForm
from xprez.models.mixins.font_size import FontSizeModuleMixin
from xprez.models.multi_module import MultiModuleItem, UploadMultiModule


class FilesModule(FontSizeModuleMixin, UploadMultiModule):
    front_template_name = "xprez/modules/files.html"
    admin_template_name = "xprez/admin/modules/files/files.html"
    admin_item_template_name = "xprez/admin/modules/files/files_item.html"
    admin_form_class = "xprez.modules.files.FilesModuleForm"
    admin_item_form_class = "xprez.modules.files.FilesItemForm"
    admin_icon_template_name = "xprez/admin/icons/modules/files.html"

    title = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Files"


class FilesItem(MultiModuleItem):
    module = models.ForeignKey(
        FilesModule, related_name="items", on_delete=models.CASCADE
    )
    file = models.FileField(upload_to="files", max_length=300)
    description = models.CharField(max_length=255, blank=True)

    def get_description(self):
        return self.description or self.get_default_file_name()

    def get_extension(self):
        try:
            return self.file.name.split("/")[-1].split(".")[-1].lower()
        except (KeyError, IndexError):
            return ""

    def get_default_file_name(self):
        try:
            return self.file.name.split("/")[-1].split(".")[0]
        except (KeyError, IndexError):
            return "unnamed"

    @classmethod
    def create_from_file(cls, django_file, module):
        item = cls(module=module, position=module.items.count())
        item.file.save(django_file.name.split("/")[-1], django_file)
        item.save()
        return item


class FilesModuleForm(ModuleForm):
    options_fields = ModuleForm.options_fields + ("font_size",)

    class Meta:
        model = FilesModule
        fields = "__all__"
        widgets = {"title": forms.TextInput(attrs={"placeholder": "Files"})}


class FilesItemForm(MultiModuleItemForm):
    class Meta:
        model = FilesItem
        fields = ("description",)
