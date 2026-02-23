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


class SyncFieldsMixin:
    SYNC_UNSAFE_WIDGETS = (forms.FileInput, forms.ClearableFileInput)
    sync_exclude = ()

    def sync_candidate_fields(self):
        """Return iterable of field names to consider for syncing."""
        raise NotImplementedError()

    def _sync_is_safe(self, field):
        return (field not in self.sync_exclude) and (
            not isinstance(self.fields[field].widget, self.SYNC_UNSAFE_WIDGETS)
        )

    @property
    def sync_fields(self):
        return tuple(
            field for field in self.sync_candidate_fields if self._sync_is_safe(field)
        )


class DeletableFormMixin:
    """Forms with delete capability skip validation when delete=True."""

    system_fields = ("delete",)
    sync_fields = ()

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


class ModuleForm(
    SyncFieldsMixin, DeletableFormMixin, PositionFormMixin, forms.ModelForm
):
    base_module_fields = (
        "position",
        "section",
    )
    system_fields = DeletableFormMixin.system_fields + ("sync_selected",)

    options_fields = (
        "alternate_color",
        "css_class",
    )

    @property
    def sync_candidate_fields(self):
        return self.options_fields

    def get_main_fields(self):
        excluded_fields = tuple(self.base_module_fields) + self.options_fields + self.system_fields
        return [self[field] for field in self.fields if field not in excluded_fields]

    def get_options_fields(self):
        return [self[field] for field in self.options_fields if field in self.fields]

    class Meta:
        fields = "__all__"


class MultiModuleItemForm(DeletableFormMixin, forms.ModelForm):
    """Base form for items within MultiModule modules."""

    def get_main_fields(self):
        for name in self.fields:
            if name not in self.system_fields:
                yield self[name]

    class Meta:
        fields = "__all__"


class ModuleConfigForm(SyncFieldsMixin, DeletableFormMixin, forms.ModelForm):
    base_module_fields = (
        "visible",
        # Grid
        "colspan",
        "rowspan",
        "order",
        "vertical_align_grid",
        "horizontal_align_grid",
        # Box
        "background",
        "border",
        "background_color",
        "padding_top_choice",
        "padding_top_custom",
        "padding_bottom_choice",
        "padding_bottom_custom",
        "padding_left_choice",
        "padding_left_custom",
        "padding_right_choice",
        "padding_right_custom",
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

    @property
    def extra_fields(self):
        excluded_fields = self.base_module_fields + self.system_fields
        return tuple(name for name in self.fields if name not in excluded_fields)

    def get_extra_fields(self):
        return tuple(self[name] for name in self.extra_fields)

    @property
    def sync_candidate_fields(self):
        return self.base_module_fields + self.extra_fields

    class Meta:
        fields = "__all__"
