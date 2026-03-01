import json

from django import forms

from xprez import constants
from xprez.conf import settings


class ShortcutsForm(forms.Form):
    def __init__(self, config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config

        for field_name, field_config in self.config.items():
            self.add_field(field_name, field_config)

    def add_field(self, field_name, field_config):
        if "clone" in field_config:
            clone_field = field_config["clone"]
            choices = list(
                getattr(settings, "XPREZ_SECTION_SHORTCUT_CLONE_CHOICES", {}).get(
                    clone_field, ()
                )
            )
            shortcut_attrs = {"clone": clone_field}
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
            choices += [(constants.CUSTOM, "Custom")]

        self.fields[field_name] = forms.ChoiceField(
            label=field_config["label"],
            choices=choices,
            widget=forms.Select(attrs={"data-shortcut": json.dumps(shortcut_attrs)}),
        )
