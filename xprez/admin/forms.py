from django import forms

from xprez.models.configs import SectionConfig
from xprez.models.sections import Section


class DeletableFormMixin:
    """Forms with delete capability skip validation when delete=True."""

    system_fields = ("delete",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["delete"] = forms.BooleanField(required=False)

    def full_clean(self):
        super().full_clean()
        if getattr(self, "cleaned_data", {}).get("delete"):
            self._errors = {}


class SectionForm(DeletableFormMixin, forms.ModelForm):
    class Meta:
        model = Section
        fields = "__all__"


class SectionConfigForm(DeletableFormMixin, forms.ModelForm):
    class Meta:
        model = SectionConfig
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.is_default():
            self.fields.pop("delete", None)


class BaseModuleForm(DeletableFormMixin, forms.ModelForm):
    base_module_fields = (
        "position",
        "section",
        "css_class",
    )

    options_fields = ()

    def get_main_fields(self):
        excluded_fields = tuple(self.base_module_fields)
        excluded_fields += self.options_fields
        excluded_fields += self.system_fields

        for field in self.fields:
            if field not in excluded_fields:
                yield self[field]

    def get_options_fields(self):
        for field in self.options_fields:
            yield self[field]

    class Meta:
        fields = "__all__"


class ModuleConfigForm(DeletableFormMixin, forms.ModelForm):
    base_module_fields = (
        "visible",
        "colspan",
        "rowspan",
        "vertical_align",
        "horizontal_align",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.is_default():
            self.fields.pop("delete", None)

    def get_extra_fields(self):
        excluded_fields = tuple(self.base_module_fields) + self.system_fields
        for field in self.fields:
            if field not in excluded_fields:
                yield self[field]

    class Meta:
        fields = "__all__"
