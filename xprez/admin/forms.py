from django import forms

from xprez.models.configs import SectionConfig
from xprez.models.sections import Section


class PositionFormMixin:
    def get_position(self):
        """
        To correctly sort sections and modules, even if they are not saved yet.
        Get position: cleaned_data > raw data > instance.
        """
        if hasattr(self, "cleaned_data") and "position" in self.cleaned_data:
            return self.cleaned_data["position"] or 0

        if self.data:
            position_key = f"{self.prefix}-position"
            try:
                return int(self.data.get(position_key, self.instance.position) or 0)
            except (ValueError, TypeError):
                pass

        return self.instance.position or 0


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


class SectionForm(DeletableFormMixin, PositionFormMixin, forms.ModelForm):
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


class BaseModuleForm(DeletableFormMixin, PositionFormMixin, forms.ModelForm):
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
        # Grid
        "colspan",
        "rowspan",
        "vertical_align_grid",
        "horizontal_align_grid",
        # Box
        "background",
        "border",
        "padding_top_choice",
        "padding_top_custom",
        "padding_bottom_choice",
        "padding_bottom_custom",
        "padding_left_choice",
        "padding_left_custom",
        "padding_right_choice",
        "padding_right_custom",
        "padding_y_linked",
        "padding_x_linked",
        "vertical_align_flex",
        "horizontal_align_flex",
        "aspect_ratio",
        "border_radius_choice",
        "border_radius_custom",
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
