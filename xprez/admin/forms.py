from django import forms

from xprez.models.configs import SectionConfig
from xprez.models.sections import Section


class SectionForm(forms.ModelForm):
    delete = forms.BooleanField(required=False)

    class Meta:
        model = Section
        fields = "__all__"


class SectionConfigForm(forms.ModelForm):
    delete = forms.BooleanField(required=False)

    class Meta:
        model = SectionConfig
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.is_default():
            del self.fields["delete"]


class BaseModuleForm(forms.ModelForm):
    delete = forms.BooleanField(required=False)

    base_module_fields = (
        "position",
        "section",
        "css_class",
        "delete",
    )

    options_fields = ()

    def get_main_fields(self):
        excluded_fields = tuple(self.base_module_fields)
        excluded_fields += self.options_fields

        for field in self.fields:
            if field not in excluded_fields:
                yield self[field]

    def get_options_fields(self):
        for field in self.options_fields:
            yield self[field]

    class Meta:
        fields = "__all__"


class ModuleConfigForm(forms.ModelForm):
    base_module_fields = (
        "visible",
        "colspan",
        "rowspan",
        "vertical_align",
        "horizontal_align",
    )

    def get_extra_fields(self):
        for field in self.fields:
            if field not in self.base_module_fields:
                yield self[field]

    class Meta:
        fields = "__all__"
