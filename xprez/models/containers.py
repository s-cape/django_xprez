from collections import defaultdict

from django.apps import apps
from django.db import models
from django.db.models import Prefetch
from django.template.loader import render_to_string
from django.utils.functional import cached_property

from xprez import constants
from xprez.models.mixins.cache import FrontCacheMixin
from xprez.utils import class_content_type


class Container(FrontCacheMixin, models.Model):
    """Base container class for pages/articles that contain modules."""

    KEY = constants.CONTAINER_KEY
    front_template_name = "xprez/container.html"

    content_type = models.CharField(max_length=100, editable=False)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.content_type = class_content_type(self.__class__)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.invalidate_front_cache()
        super().delete(*args, **kwargs)

    @cached_property
    def front_cacheable(self):
        return all(s.front_cacheable for s in self.get_sections_front())

    @cached_property
    def polymorph(self):
        app_label, object_name = self.content_type.split(".")
        model = apps.get_model(app_label, object_name)
        if isinstance(self, model):
            return self
        else:
            return model.objects.get(pk=self.pk)

    def duplicate_to(self, target_container, saved=False, allowed_module_classes=None):
        """Duplicate this container into target_container. Returns list of created sections and section symlinks (sections first, then symlinks, each ordered by position)."""
        result = []
        for section in self.sections.all().order_by("position"):
            new_section = section.duplicate_to(
                target_container,
                saved=saved,
                allowed_module_classes=allowed_module_classes,
            )
            result += [new_section]
        for symlink in self.sectionsymlinks.all().order_by("position"):
            new_symlink = symlink.duplicate_to(target_container, saved=saved)
            result += [new_symlink]
        return result

    def symlink_to(self, target_container, saved=False):
        """Create SectionSymlinks in target_container; returns them (sections then symlinks, by position)."""
        result = []
        for section in self.sections.filter(saved=True).order_by("position"):
            new_symlink = section.symlink_to(target_container, saved=saved)
            result += [new_symlink]
        for symlink in self.sectionsymlinks.filter(saved=True).order_by("position"):
            new_symlink = symlink.symlink_to(target_container, saved=saved)
            result += [new_symlink]
        return result

    def clipboard_verbose_name(self):
        return self.polymorph._meta.verbose_name

    def preview_text(self):
        return self.polymorph.__str__()

    def render_front(self, context):
        self.preload_front_structure()
        context["container"] = self.polymorph
        return render_to_string(self.front_template_name, context)

    def get_sections_front(self):
        if not hasattr(self, "_sections_front"):
            sections = list(self.sections.filter(saved=True, visible=True))
            symlinks = list(self.sectionsymlinks.filter(saved=True, visible=True))
            self._sections_front = sorted(sections + symlinks, key=lambda s: s.position)
        return self._sections_front

    def preload_front_structure(self):
        """Bulk-load all frontend data, populating _*_front caches before rendering."""
        from xprez.models.configs import SectionConfig
        from xprez.models.modules import Module

        section_config_qs = SectionConfig.objects.filter(saved=True).order_by(
            "css_breakpoint"
        )
        module_qs = Module.objects.filter(saved=True).order_by("position")

        # Phase 1: sections + SectionConfigs + base modules (3-4 queries)
        sections = list(
            self.sections.filter(saved=True, visible=True).prefetch_related(
                Prefetch("configs", queryset=section_config_qs),
                Prefetch("modules", queryset=module_qs),
            )
        )
        symlinks = list(
            self.sectionsymlinks.filter(saved=True, visible=True)
            .select_related("symlink")
            .prefetch_related(
                Prefetch("symlink__configs", queryset=section_config_qs),
                Prefetch("symlink__modules", queryset=module_qs),
            )
        )

        # Deduplicate symlinked sections against already-loaded sections
        seen_section_pks = {s.pk for s in sections}
        extra_sections = []
        for sl in symlinks:
            if sl.symlink and sl.symlink.pk not in seen_section_pks:
                seen_section_pks.add(sl.symlink.pk)
                extra_sections += [sl.symlink]
        all_sections = sections + extra_sections

        # Phase 2: resolve polymorphic modules (1 query per content type)
        all_base_modules = [
            m for section in all_sections for m in section.modules.all()
        ]

        polymorph_by_pk = {}
        if all_base_modules:
            pks_by_content_type = defaultdict(list)
            for m in all_base_modules:
                pks_by_content_type[m.content_type] += [m.pk]
            for content_type, pks in pks_by_content_type.items():
                ct_app, ct_model = content_type.split(".")
                model_class = apps.get_model(ct_app, ct_model)
                for instance in model_class.objects.filter(pk__in=pks):
                    polymorph_by_pk[instance.pk] = instance

        # Phase 3: module configs, one query per config model
        pks_by_config_model = defaultdict(list)
        for module in polymorph_by_pk.values():
            pks_by_config_model[module.config_model] += [module.pk]

        configs_by_module_pk = defaultdict(list)
        for config_model_path, pks in pks_by_config_model.items():
            cfg_app, cfg_model = config_model_path.split(".")
            config_model = apps.get_model(cfg_app, cfg_model)
            for config in config_model.objects.filter(
                module_id__in=pks, saved=True
            ).order_by("css_breakpoint"):
                configs_by_module_pk[config.module_id] += [config]

        # Phase 4: populate _*_front caches on all sections and modules
        for section in all_sections:
            section._configs_front = list(section.configs.all())
            section._modules_front = [
                polymorph_by_pk[m.pk]
                for m in section.modules.all()
                if m.pk in polymorph_by_pk
            ]
            for module in section._modules_front:
                module._configs_front = configs_by_module_pk.get(module.pk, [])

        self._sections_front = sorted(sections + symlinks, key=lambda s: s.position)
