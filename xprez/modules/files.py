from django import forms
from django.db import models
from django.forms import inlineformset_factory

from xprez.admin.forms import BaseModuleForm
from xprez.models.modules import MultiModuleItem, UploadMultiModule


class FilesModule(UploadMultiModule):
    admin_template_name = "xprez/admin/modules/files/files.html"
    front_template_name = "xprez/modules/files.html"
    admin_formset_item_template_name = "xprez/admin/modules/files/files_item.html"
    icon_template_name = "xprez/admin/icons/modules/files.html"
    form_class = "xprez.modules.files.FilesModuleForm"
    formset_factory = "xprez.modules.files.FilesItemFormSet"

    title = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Files"

    def render_front(self, context):
        if self.items.all().exists():
            return super().render_front(context)
        else:
            return ""


class FilesItem(MultiModuleItem):
    module = models.ForeignKey(
        FilesModule, related_name="items", on_delete=models.CASCADE
    )
    file = models.FileField(upload_to="files", max_length=300)
    description = models.CharField(max_length=255, blank=True)
    position = models.PositiveSmallIntegerField()

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
        att = cls(module=module)
        att.position = module.attachments.all().count()
        att.file.save(django_file.name.split("/")[-1], django_file)
        att.save()
        return att

    class Meta:
        ordering = ("position",)


class FilesModuleForm(BaseModuleForm):
    class Meta:
        model = FilesModule
        fields = ("title",) + BaseModuleForm.base_module_fields
        widgets = {"title": forms.TextInput(attrs={"placeholder": "Files"})}


FilesItemFormSet = inlineformset_factory(
    FilesModule,
    FilesItem,
    fields=("id", "description", "position"),
    extra=0,
    can_delete=True,
)
