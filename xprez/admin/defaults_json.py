import json

from xprez import module_registry, settings
from xprez.models import Section
from xprez.utils import import_class


class XprezAdminDefaultsJsonMixin:
    """Mixin for generating JS defaults JSON."""

    def xprez_defaults_json(self):
        """Returns defaults as JSON, built from actual instances."""
        section = Section()
        section_config = section.build_config(settings.XPREZ_DEFAULT_BREAKPOINT)

        module_defaults = {}
        module_config_defaults = {}
        for module_class in module_registry._registry.values():
            module = module_class.build()
            ct = module_class.class_content_type()
            module_defaults[ct] = self._instance_defaults(module)
            module_config_defaults[ct] = self._instance_defaults(
                module.build_config(settings.XPREZ_DEFAULT_BREAKPOINT)
            )

        return json.dumps(
            {
                "section": self._instance_defaults(
                    section, import_class("xprez.admin.forms.SectionForm")
                ),
                "section_config": self._instance_defaults(section_config),
                "module": module_defaults,
                "module_config": module_config_defaults,
            }
        )

    def _instance_defaults(self, instance, form_class=None):
        """Extract defaults from instance using its admin form or specified form class."""
        form_class = form_class or instance.get_admin_form_class()
        form = form_class(instance=instance)
        defaults = {}
        for name in form.fields:
            value = form.initial.get(name)
            # Skip non-JSON-serializable values (like FieldFile)
            if value is None or isinstance(value, (str, int, float, bool)):
                defaults[name] = value
        return defaults
