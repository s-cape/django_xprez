from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext

from xprez import constants
from xprez.admin.forms import ModuleForm, MultiModuleItemForm
from xprez.ck_editor.forms import CkEditorFileUploadFormMixin
from xprez.conf import settings as xprez_settings
from xprez.models.mixins.font_size import FontSizeModuleMixin
from xprez.models.multi_module import MultiModule, MultiModuleItem
from xprez.utils import import_class


class AccordionModule(FontSizeModuleMixin, MultiModule):
    front_template_name = "xprez/modules/accordion.html"
    admin_template_name = "xprez/admin/modules/accordion/accordion.html"
    admin_item_template_name = "xprez/admin/modules/accordion/accordion_item.html"
    admin_item_form_class = "xprez.modules.accordion.AccordionItemForm"
    admin_form_class = "xprez.modules.files.FilesModuleForm"
    admin_icon_template_name = "xprez/shared/icons/modules/accordion.html"

    class Meta:
        verbose_name = _("Accordion")

    class FrontMedia:
        js = ("xprez/js/accordion.min.js",)

    def save(self, *args, **kwargs):
        no_initial_item = kwargs.pop("no_initial_item", False)
        is_new = not self.pk
        super().save(*args, **kwargs)
        if is_new and not no_initial_item:
            self.create_item(saved=True)

    def duplicate_to(self, target_section, saved=constants.SAVED_FORCE_FALSE, **kwargs):
        kwargs["no_initial_item"] = True
        return super().duplicate_to(target_section, saved=saved, **kwargs)

    def preview_text(self):
        count = self.items.count()
        return ngettext("%(count)s item", "%(count)s items", count) % {"count": count}


class AccordionItem(MultiModuleItem):
    module = models.ForeignKey(
        AccordionModule,
        related_name="items",
        on_delete=models.CASCADE,
        editable=False,
    )
    title = models.CharField(_("Title"), max_length=255, blank=True)
    text = models.TextField(_("Text"), blank=True)


class AccordionItemForm(CkEditorFileUploadFormMixin, MultiModuleItemForm):
    def xprez_ckeditor_file_upload_url_name(self):
        return xprez_settings.XPREZ_CK_EDITOR_FILE_UPLOAD_URL_NAME

    def xprez_ckeditor_file_upload_dir(self):
        return xprez_settings.XPREZ_CK_EDITOR_FILE_UPLOAD_DIR

    class Meta(MultiModuleItemForm.Meta):
        model = AccordionItem
        fields = "__all__"
        widgets = {
            "text": import_class(xprez_settings.XPREZ_CK_EDITOR_MODULE_WIDGET)(),
        }


class AccordionModuleForm(ModuleForm):
    options_fields = ModuleForm.options_fields + ("font_size",)
