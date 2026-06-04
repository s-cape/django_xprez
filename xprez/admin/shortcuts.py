import json

from django import forms
from django.db import models


class ShortcutsMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.shortcuts_config:
            self.shortcuts = ShortcutsForm(self, prefix=f"{self.prefix}-shortcuts")
        else:
            self.shortcuts = None


class ShortcutsForm(forms.Form):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = parent

        for field_name, field_config in self.parent.shortcuts_config.items():
            self.add_field(field_name, field_config)

    def add_field(self, field_name, field_config):
        if "clone" in field_config:
            clone_field = field_config["clone"]
            model_field = self.parent.instance._meta.get_field(clone_field)
            label = field_config.get("label") or model_field.verbose_name
            shortcut_attrs = {"clone": clone_field}
            if isinstance(model_field, models.BooleanField):
                self._add_field_boolean(
                    field_name, {**field_config, "label": label}, shortcut_attrs
                )
            else:
                self._add_field_choices(
                    field_name,
                    {**field_config, "label": label},
                    list(model_field.choices),
                    shortcut_attrs,
                )
        else:
            choices = []
            shortcut_attrs = {}
            for choice in field_config["choices"]:
                value, label, config = (
                    choice["value"],
                    choice["label"],
                    choice["config"],
                )
                choices += [(value, label)]
                for fname, breakpoint_map in config.items():
                    shortcut_attrs.setdefault(fname, {})[value] = breakpoint_map
            choices += [("advanced", "Advanced")]
            self._add_field_choices(field_name, field_config, choices, shortcut_attrs)

    def _add_field_boolean(self, field_name, field_config, shortcut_attrs):
        self.fields[field_name] = forms.BooleanField(
            label=field_config["label"],
            required=False,
            widget=forms.CheckboxInput(
                attrs={"data-shortcut": json.dumps(shortcut_attrs)}
            ),
        )

    def _add_field_choices(self, field_name, field_config, choices, shortcut_attrs):
        self.fields[field_name] = forms.ChoiceField(
            label=field_config["label"],
            choices=choices,
            widget=forms.Select(attrs={"data-shortcut": json.dumps(shortcut_attrs)}),
        )
