from django import forms
from django.db import models
from django.forms import inlineformset_factory

from xprez.admin.forms import BaseModuleForm
from xprez.models.modules import MultiModuleItem, UploadMultiModule


class DownloadsModule(UploadMultiModule):
    admin_template_name = "xprez/admin/modules/downloads/downloads.html"
    front_template_name = "xprez/modules/downloads.html"
    admin_formset_item_template_name = (
        "xprez/admin/modules/downloads/downloads_item.html"
    )
    icon_template_name = "xprez/admin/icons/modules/downloads.html"
    form_class = "xprez.modules.downloads.DownloadsModuleForm"
    formset_factory = "xprez.modules.downloads.DownloadsItemFormSet"

    title = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Files"

    def render_front(self, context):
        if self.items.all().exists():
            return super().render_front(context)
        else:
            return ""


class DownloadsItem(MultiModuleItem):
    module = models.ForeignKey(
        DownloadsModule, related_name="items", on_delete=models.CASCADE
    )
    file = models.FileField(upload_to="files", max_length=300)
    name = models.CharField(max_length=100, blank=True)
    position = models.PositiveSmallIntegerField()

    def get_name(self):
        return self.name or self.get_default_file_name()

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


class DownloadsModuleForm(BaseModuleForm):
    class Meta:
        model = DownloadsModule
        fields = ("title",) + BaseModuleForm.base_module_fields
        widgets = {"title": forms.TextInput(attrs={"placeholder": "Files"})}


DownloadsItemFormSet = inlineformset_factory(
    DownloadsModule,
    DownloadsItem,
    fields=("id", "name", "position"),
    extra=0,
    can_delete=True,
)
