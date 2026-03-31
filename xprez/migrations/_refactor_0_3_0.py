"""
Custom migration operations and processor bases for the 0.3.0 refactor.

Operations handle inheritance changes that Django automatic migrations can't.
Processor bases provide the framework for migrating old Content models to new
Module models; user code can subclass these for custom module processors.

Reference:
`https://stackoverflow.com/questions/61665607/renaming-a-django-superclass-model-and-updating-the-subclass-pointers-correctly`
"""

import re

from django.core.management.color import no_style
from django.db import migrations, models
from django.db.migrations.operations.base import Operation
from django.utils import timezone


def _get_settings(name):
    """Lazy-load setting (avoids import-time issues during migration collection)."""
    from xprez.conf import settings

    return getattr(settings, name)


def _content_type(obj):
    return "{}.{}".format(
        obj._meta.app_label,
        obj._meta.object_name,
    )


# ---------------------------------------------------------------------------
# Migration operations
# ---------------------------------------------------------------------------


class InheritanceChangeOperation(Operation):
    """
    Rename an auto-created multi-table inheritance ptr field and repoint it to
    a different parent model (also updates the child's bases).

    This operation intentionally uses ProjectState helpers (`rename_field`,
    `alter_field`) to ensure Django reloads the in-memory app registry for the
    mutated model, so later operations in the same migration see the new field.
    """

    reversible = False

    def __init__(
        self,
        model_name,
        *,
        from_field_name,
        to_field_name,
        from_remote_model,
        to_remote_model,
    ):
        self.model_name = model_name
        self.from_field_name = from_field_name
        self.to_field_name = to_field_name
        self.from_remote_model = from_remote_model
        self.to_remote_model = to_remote_model

    @staticmethod
    def _replace_base(bases, from_remote_model, to_remote_model):
        from_remote_model = from_remote_model.lower()
        new_bases = []
        for base in bases:
            if isinstance(base, str) and base.lower() == from_remote_model:
                new_bases.append(to_remote_model)
            else:
                new_bases.append(base)
        return tuple(new_bases)

    def _render_as_plain_model(self, app_label, from_state):
        """
        Render the child model without inheritance bases.

        Without this, Django's historical model rendering can error while the
        parent/ptr relationship is in a transitional state.
        """
        renderable_from_state = from_state.clone()
        renderable_from_state.models[app_label, self.model_name.lower()].bases = (
            models.Model,
        )
        return renderable_from_state

    def state_forwards(self, app_label, state):
        model_name = self.model_name.lower()
        state.rename_field(
            app_label, model_name, self.from_field_name, self.to_field_name
        )
        model_state = state.models[app_label, model_name]
        model_state.bases = self._replace_base(
            model_state.bases,
            from_remote_model=self.from_remote_model,
            to_remote_model=self.to_remote_model,
        )
        new_field = model_state.fields[self.to_field_name].clone()
        new_field.remote_field.model = self.to_remote_model
        new_field.name = self.to_field_name
        state.alter_field(
            app_label,
            model_name,
            self.to_field_name,
            new_field,
            preserve_default=True,
        )

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        to_model = to_state.apps.get_model(app_label, self.model_name)
        renderable_from_state = self._render_as_plain_model(app_label, from_state)
        from_model = renderable_from_state.apps.get_model(app_label, self.model_name)
        from_field = from_model._meta.get_field(self.from_field_name)
        to_field = to_model._meta.get_field(self.to_field_name)
        schema_editor.alter_field(from_model, from_field, to_field)


class ContentToModule(InheritanceChangeOperation):
    """
    Rename content_ptr to module_ptr and update the field reference.
    Changes parent inheritance from Content to Module.
    Needed for migration of custom contents to modules at 0.3.0.
    """

    def __init__(self, model_name):
        super().__init__(
            model_name,
            from_field_name="content_ptr",
            to_field_name="module_ptr",
            from_remote_model="xprez.content",
            to_remote_model="xprez.module",
        )


class ContentsContainerToContainer(InheritanceChangeOperation):
    """
    Rename contentscontainer_ptr to container_ptr and update the field reference.
    Changes parent inheritance from ContentsContainer to Container.
    Needed for migration to 0.3.0.
    """

    def __init__(self, model_name):
        super().__init__(
            model_name,
            from_field_name="contentscontainer_ptr",
            to_field_name="container_ptr",
            from_remote_model="xprez.contentscontainer",
            to_remote_model="xprez.container",
        )


# ---------------------------------------------------------------------------
# Built-in model renames (old Content name -> new Module name)
# ---------------------------------------------------------------------------

RENAMES = {
    "Gallery": "GalleryModule",
    "CodeInput": "CodeInputModule",
    "CodeTemplate": "CodeTemplateModule",
    "DownloadContent": "FilesModule",
    "NumbersContent": "NumbersModule",
    "Video": "VideoModule",
    "ContentSymlink": "ModuleSymlink",
}

RENAMES_LOWER = {k.lower(): v for k, v in RENAMES.items()}


# ---------------------------------------------------------------------------
# Module processor bases
# ---------------------------------------------------------------------------


class ModuleProcessorBase:
    old_content_class = None

    WIDTH_TRANS = {
        "full": "full",
        "mid": "medium",
        "text": "small",
    }

    def __init__(self, apps, module_base):
        self.apps = apps
        self.module_base = module_base
        self.module_class = self.apps.get_model(*module_base.content_type.split("."))
        self.module = self.module_class.objects.get(id=module_base.id)
        self.load_old_content()

    def load_old_content(self):
        Content = self.apps.get_model("xprez", "Content")
        self.old_content_base = Content.objects.get(id=self.module_base.id)

        old_content_attr = self.old_content_base.content_type.lower()
        if old_content_attr in RENAMES_LOWER:
            old_content_class = self.apps.get_model(
                "xprez", RENAMES_LOWER[old_content_attr]
            )
        else:
            app_label, model_name = self.module_base.content_type.split(".", 1)
            old_content_class = self.apps.get_model(app_label, model_name)
        self.old_content = old_content_class.objects.get(id=self.old_content_base.id)

    def process(self):
        raise NotImplementedError()

    def get_config_class(self, module):
        return "xprez.ModuleConfig"

    def finalize(self, module):
        """Create/get module config from defaults. Subclasses override to map old_content to module/config."""
        default_breakpoint = 0
        xprez_defaults = _get_settings("XPREZ_DEFAULTS")
        config_class = self.apps.get_model(*self.get_config_class(module).split("."))
        default_config = xprez_defaults["module_config"]["default"]
        self.config, _created = config_class.objects.get_or_create(
            module=module,
            css_breakpoint=default_breakpoint,
            defaults={
                "saved": True,
                "colspan": default_config["colspan"],
                "rowspan": default_config["rowspan"],
                "vertical_align_grid": default_config["vertical_align_grid"],
                "horizontal_align_grid": default_config["horizontal_align_grid"],
                "vertical_align_flex": default_config["vertical_align_flex"],
                "horizontal_align_flex": default_config["horizontal_align_flex"],
                "border_radius_choice": default_config["border_radius_choice"],
                "border_radius_custom": default_config["border_radius_custom"],
                "background": default_config["background"],
                "background_color": default_config["background_color"],
                "border": default_config["border"],
                "padding_left_choice": default_config["padding_left_choice"],
                "padding_left_custom": default_config["padding_left_custom"],
                "padding_right_choice": default_config["padding_right_choice"],
                "padding_right_custom": default_config["padding_right_custom"],
                "padding_top_choice": default_config["padding_top_choice"],
                "padding_top_custom": default_config["padding_top_custom"],
                "padding_bottom_choice": default_config["padding_bottom_choice"],
                "padding_bottom_custom": default_config["padding_bottom_custom"],
                "aspect_ratio": default_config["aspect_ratio"],
            },
        )


class SimpleModuleProcessor(ModuleProcessorBase):
    def process(self):
        self.finalize(self.module)


class ModuleReplaceProcessor(ModuleProcessorBase):
    """Replace a module with new module(s)."""

    def process(self):
        self.new_modules = self.prepare_new_modules()
        self.finalize_new_modules()
        self.delete_replaced_module()

    def prepare_new_modules(self):
        """Return list of new module instances (unsaved). Subclasses must implement."""
        raise NotImplementedError()

    def finalize_new_modules(self):
        """Save each new module to DB and call finalize(module) for each."""
        for new_module in self.new_modules:
            new_module.content_type = _content_type(new_module)
            new_module.section = self.module_base.section
            new_module.saved = True
            new_module.created = timezone.now()
            new_module.changed = timezone.now()
            new_module.save()
            self.finalize(new_module)

    def delete_replaced_module(self):
        """Remove the original module that was replaced by new_modules."""
        self.module_base.delete()


class WidthModuleProcessorMixin:
    """Migrate old_content.width to section.max_width_choice."""

    def process(self):
        super().process()
        section = self.module.section
        section.max_width_choice = self.WIDTH_TRANS.get(
            getattr(self.old_content, "width", "full"), "full"
        )
        section.save()


class BreakpointColumnsMixin:
    def _columns_shortcut_choices(self):
        raise NotImplementedError()

    def _get_columns_by_breakpoint(self, num_columns):
        for choice in self._columns_shortcut_choices():
            if choice["value"] == num_columns:
                return choice["config"]["columns"]
        return {0: num_columns}

    def _create_breakpoint_configs(self, config_0, columns_by_breakpoint):
        """Clone config_0 for each non-zero breakpoint with a distinct column count."""
        from xprez.utils import copy_model

        previous_columns = config_0.columns
        for breakpoint, columns in columns_by_breakpoint.items():
            if breakpoint == 0:
                continue
            if previous_columns == columns:
                continue
            previous_columns = columns
            bp_config = copy_model(config_0)
            bp_config.css_breakpoint = breakpoint
            bp_config.columns = columns
            bp_config.save()


class BoxModuleProcessorMixin:
    """Migrate old_content.box to config background and padding."""

    def finalize(self, module):
        super().finalize(module)
        if getattr(self.old_content, "box", False):
            self.config.background = True
            self.config.padding_left_choice = "medium"
            self.config.padding_right_choice = "medium"
            self.config.padding_top_choice = "medium"
            self.config.padding_bottom_choice = "medium"
            self.config.save()


class ExtractImageMixin:
    IMG_BLOCK_RE = re.compile(
        r"^\s*<(?:p|figure)[^>]*>\s*(?:<a\s([^>]*)>\s*)?(<img\s[^>]*?/?>)\s*(?:</a>\s*)?</(?:p|figure)>\s*",
        re.I | re.S,
    )
    IMG_RE = re.compile(r"^\s*(<img\s[^>]*?/?>)\s*", re.I | re.S)
    # <hN>…<img>…rest…</hN> (image first inside heading; keep rest inside the heading)
    IMG_HEADING_RE = re.compile(
        r"^\s*(<h([1-6])[^>]*>)\s*(?:<a\s([^>]*)>\s*)?(<img\s[^>]*?/?>)\s*(?:</a>\s*)?(.*?)</h\2>\s*",
        re.I | re.S,
    )
    # <p>…<img>…rest…</p>
    IMG_PARAGRAPH_RE = re.compile(
        r"^\s*(<p[^>]*>)\s*(?:<a\s([^>]*)>\s*)?(<img\s[^>]*?/?>)\s*(?:</a>\s*)?(.*?)</p>\s*",
        re.I | re.S,
    )
    _EMPTY_P_RE = re.compile(
        r"^\s*<p[^>]*>\s*(?:&nbsp;|&#160;|&#xa0;|\s)*</p>\s*",
        re.I | re.S,
    )
    SRC_RE = re.compile(r'\bsrc=["\']([^"\']+)["\']', re.I)
    HREF_RE = re.compile(r'\bhref=["\']([^"\']+)["\']', re.I)

    @staticmethod
    def extract_image(text):
        """-> (relative_media_path, url, remaining_text) or (None, None, text)"""
        from django.conf import settings as django_settings

        E = ExtractImageMixin
        media_url = django_settings.MEDIA_URL

        def _local_media(anchor_attrs, img_tag):
            src_m = E.SRC_RE.search(img_tag)
            if src_m:
                src = src_m.group(1)
                if src.startswith(media_url):
                    url = None
                    if anchor_attrs:
                        href_m = E.HREF_RE.search(anchor_attrs)
                        if href_m:
                            url = href_m.group(1)
                    return src[len(media_url) :], url
                else:
                    return None, None
            else:
                return None, None

        # Strip leading empty <p> tags (e.g. <p>&nbsp;</p>)
        prefix = ""
        work = text
        while True:
            empty_p = E._EMPTY_P_RE.match(work)
            if empty_p:
                prefix += work[: empty_p.end()]
                work = work[empty_p.end() :]
            else:
                break

        path = url = None
        remaining = text

        # Standalone image block: <figure> or <p> containing only <img>
        m = E.IMG_BLOCK_RE.match(work)
        if m:
            path, url = _local_media(m.group(1), m.group(2))
            if path is not None:
                remaining = prefix + work[m.end() :]

        # Bare <img> at start
        if path is None:
            m = E.IMG_RE.match(work)
            if m:
                path, url = _local_media(None, m.group(1))
                if path is not None:
                    remaining = prefix + work[m.end() :]

        # <hN><img …>rest…</hN> — extract image, keep rest in the heading
        if path is None:
            m = E.IMG_HEADING_RE.match(work)
            if m:
                path, url = _local_media(m.group(3), m.group(4))
                if path is not None:
                    remaining = (
                        prefix
                        + m.group(1)
                        + m.group(5)
                        + "</h"
                        + m.group(2)
                        + ">"
                        + work[m.end() :]
                    )

        # <p><img …>rest…</p> — extract image, keep rest in the paragraph
        if path is None:
            m = E.IMG_PARAGRAPH_RE.match(work)
            if m:
                path, url = _local_media(m.group(2), m.group(3))
                if path is not None:
                    remaining = (
                        prefix + m.group(1) + m.group(4) + "</p>" + work[m.end() :]
                    )

        return path, url, remaining


# ---------------------------------------------------------------------------
# RunPython callables
# ---------------------------------------------------------------------------


def _reset_sequences(schema_editor, models_list):
    """
    When we insert rows with explicit PKs (e.g. id=old_id), Postgres sequences
    may remain behind; later inserts that rely on the sequence can then collide.
    """
    for sql in schema_editor.connection.ops.sequence_reset_sql(no_style(), models_list):
        schema_editor.execute(sql)


def migrate_containers_sections_modules(apps, schema_editor):
    xprez_defaults = _get_settings("XPREZ_DEFAULTS")
    section_defaults = xprez_defaults["section"]
    section_config_defaults = xprez_defaults["section_config"]
    module_defaults = xprez_defaults["module"]["default"]

    ContentsContainer = apps.get_model("xprez", "ContentsContainer")
    Content = apps.get_model("xprez", "Content")

    Container = apps.get_model("xprez", "Container")
    Module = apps.get_model("xprez", "Module")
    Section = apps.get_model("xprez", "Section")

    # Old Content integer spacing fields → new SectionConfig string values.
    spacing_trans = {
        0: "",
        1: "small",
        2: "medium",
        3: "large",
        4: "extra_large",
    }

    for old_container in ContentsContainer.objects.all():
        old_container_polymorph = getattr(
            old_container, old_container.content_type.lower()
        )
        container = Container.objects.create(
            id=old_container.id,
            content_type=_content_type(old_container_polymorph),
        )
        for old_content_base in Content.objects.filter(page=old_container):
            old_content = getattr(
                old_content_base, old_content_base.content_type.lower()
            )
            section = Section.objects.create(
                container=container,
                position=old_content.position,
                visible=old_content.visible,
                max_width_choice=section_defaults["max_width_choice"],
                max_width_custom=section_defaults["max_width_custom"],
                alternate_background=old_content.alternate_color,
                background_color=old_content.background_color,
                css_class=old_content.css_class,
                saved=True,
            )
            section_config, _created = section.configs.get_or_create(
                css_breakpoint=0,
                defaults={
                    "saved": True,
                    "columns": section_config_defaults["columns"],
                    "margin_bottom_choice": spacing_trans.get(
                        old_content_base.margin_bottom,
                        section_config_defaults["margin_bottom_choice"],
                    ),
                    "margin_bottom_custom": section_config_defaults[
                        "margin_bottom_custom"
                    ],
                    "padding_left_choice": section_config_defaults[
                        "padding_left_choice"
                    ],
                    "padding_left_custom": section_config_defaults[
                        "padding_left_custom"
                    ],
                    "padding_right_choice": section_config_defaults[
                        "padding_right_choice"
                    ],
                    "padding_right_custom": section_config_defaults[
                        "padding_right_custom"
                    ],
                    "padding_top_choice": spacing_trans.get(
                        old_content_base.padding_top,
                        section_config_defaults["padding_top_choice"],
                    ),
                    "padding_top_custom": section_config_defaults["padding_top_custom"],
                    "padding_bottom_choice": spacing_trans.get(
                        old_content_base.padding_bottom,
                        section_config_defaults["padding_bottom_choice"],
                    ),
                    "padding_bottom_custom": section_config_defaults[
                        "padding_bottom_custom"
                    ],
                    "gap_choice": section_config_defaults["gap_choice"],
                    "gap_custom": section_config_defaults["gap_custom"],
                    "vertical_align_grid": section_config_defaults[
                        "vertical_align_grid"
                    ],
                    "horizontal_align_grid": section_config_defaults[
                        "horizontal_align_grid"
                    ],
                },
            )

            Module.objects.create(
                id=old_content_base.id,
                content_type=_content_type(old_content),
                section=section,
                position=0,
                saved=True,
                alternate_color=module_defaults["alternate_color"],
                created=timezone.now(),
                changed=timezone.now(),
            )

    _reset_sequences(schema_editor, [Container, Module])


def rename_content_types(apps, schema_editor):
    Module = apps.get_model("xprez", "Module")
    for old_content_type, new_content_type in RENAMES.items():
        old_content_type = f"xprez.{old_content_type}"
        new_content_type = f"xprez.{new_content_type}"
        Module.objects.filter(content_type=old_content_type).update(
            content_type=new_content_type
        )


# ---------------------------------------------------------------------------
# Concrete processors for built-in modules
# ---------------------------------------------------------------------------


class TextModuleProcessorBase(
    ExtractImageMixin, BoxModuleProcessorMixin, ModuleReplaceProcessor
):
    def get_config_class(self, module):
        return "xprez.TextConfig"

    def _prepare_text_module(self, text):
        """Create an unsaved TextModule, extracting a leading local image if present."""
        TextModule = self.apps.get_model("xprez", "TextModule")
        media_path, url, cleaned_text = self.extract_image(text)
        module = TextModule(text=cleaned_text)
        if media_path:
            module.media = media_path
            module.url = url
            module._media_role = "lead"
        else:
            module._media_role = None
        return module

    def prepare_new_modules(self):
        return [self._prepare_text_module(self.old_content.text)]

    def finalize(self, module):
        super().finalize(module)
        if module._media_role:
            self.config.media_role = module._media_role
            self.config.save()

    def finalize_new_modules(self):
        super().finalize_new_modules()
        section = self.module_base.section
        section.max_width_choice = self.WIDTH_TRANS.get(
            getattr(self.old_content, "width", "full"), "full"
        )
        section.save()


class CkEditorProcessor(TextModuleProcessorBase):
    def finalize(self, module):
        super().finalize(module)
        if getattr(self.old_content, "content_centered", False):
            self.config.text_align = "center"
            self.config.save()
        if getattr(self.old_content, "alternate_color", False):
            module.alternate_color = True
            module.save()


class MediumEditorProcessor(TextModuleProcessorBase):
    pass


class GridboxesProcessor(BreakpointColumnsMixin, TextModuleProcessorBase):
    MARGIN_TRANS = {"none": "", "m": "medium", "l": "large"}
    TEXT_SIZE_TRANS = {"xs": "smallest", "s": "small", "m": "normal"}

    def prepare_new_modules(self):
        new_modules = []
        for index, box in enumerate(self.old_content.boxes or []):
            module = self._prepare_text_module(box)
            module.position = index
            new_modules += [module]
        return new_modules

    def finalize_new_modules(self):
        super().finalize_new_modules()
        section = self.module_base.section
        section.max_width_choice = self.WIDTH_TRANS.get(
            getattr(self.old_content, "width", "full"), "full"
        )
        section.save()

        columns_by_breakpoint = self._get_columns_by_breakpoint(
            self.old_content.columns
        )
        gap_choice = self.MARGIN_TRANS.get(self.old_content.margin, "medium")

        SectionConfig = self.apps.get_model("xprez", "SectionConfig")
        config_0 = SectionConfig.objects.get(section=section, css_breakpoint=0)
        config_0.columns = columns_by_breakpoint.get(0, self.old_content.columns)
        config_0.gap_choice = gap_choice
        config_0.save()

        self._create_breakpoint_configs(config_0, columns_by_breakpoint)

    def _columns_shortcut_choices(self):
        return _get_settings("XPREZ_DEFAULTS")["section_shortcuts"]["columns"][
            "choices"
        ]

    def finalize(self, module):
        super().finalize(module)
        module.font_size = self.TEXT_SIZE_TRANS.get(
            self.old_content.text_size, "normal"
        )
        module.save()

        if getattr(self.old_content, "content_centered", False):
            self.config.text_align = "center"

        if getattr(self.old_content, "padded", False):
            self.config.padding_left_choice = "medium"
            self.config.padding_right_choice = "medium"
            self.config.padding_top_choice = "medium"
            self.config.padding_bottom_choice = "medium"

        if getattr(self.old_content, "boxes_filled", False):
            self.config.background = True

        if getattr(self.old_content, "border", False):
            self.config.border = True

        image_sizing = getattr(self.old_content, "image_sizing", "fill")
        if image_sizing == "edge":
            self.config.media_role = "lead"
            self.config.media_lead_to_edge = True
        elif image_sizing == "icon":
            self.config.media_role = "icon"
            image_max_width = getattr(self.old_content, "image_max_width", None)
            if image_max_width:
                self.config.media_icon_max_size = image_max_width
        else:
            self.config.media_role = "lead"
            self.config.media_lead_to_edge = False

        self.config.save()


class QuotesProcessor(BoxModuleProcessorMixin, ModuleReplaceProcessor):
    def prepare_new_modules(self):
        QuoteModule = self.apps.get_model("xprez", "QuoteModule")
        quotes = self.old_content.quotes.all()
        if not self.old_content.display_two:
            quotes = quotes[:1]

        section = self.module_base.section
        if len(quotes) > 1:
            section.max_width_choice = "medium"
            section_config = section.configs.get(css_breakpoint=0)
            section_config.columns = 2
            section_config.save()
        else:
            section.max_width_choice = "small"
        section.save()

        new_modules = []
        for index, quote in enumerate(quotes):
            new_modules += [
                QuoteModule(
                    position=index,
                    name=quote.name,
                    subtitle=quote.job_title,
                    image=quote.image,
                    title=quote.title,
                    quote=quote.quote,
                )
            ]
        return new_modules


class TextImageProcessor(ModuleReplaceProcessor):
    def get_config_class(self, module):
        return {
            "xprez.GalleryModule": "xprez.GalleryConfig",
            "xprez.TextModule": "xprez.TextConfig",
        }[module.content_type]

    def prepare_new_modules(self):
        TextModule = self.apps.get_model("xprez", "TextModule")
        GalleryModule = self.apps.get_model("xprez", "GalleryModule")
        image_left = getattr(self.old_content, "image_alignment", "right") == "left"
        text_pos, gallery_pos = (1, 0) if image_left else (0, 1)
        modules = [
            TextModule(position=text_pos, text=self.old_content.text),
            GalleryModule(position=gallery_pos),
        ]
        return sorted(modules, key=lambda m: m.position)

    def finalize(self, module):
        super().finalize(module)
        if module.content_type == "xprez.GalleryModule":
            GalleryItem = self.apps.get_model("xprez", "GalleryItem")
            GalleryItem.objects.create(
                module=module, file=self.old_content.image, position=0, saved=True
            )
            self.config.columns = 1
            self.config.save()

    def finalize_new_modules(self):
        super().finalize_new_modules()
        section = self.module_base.section
        default_breakpoint = 0
        section_config = section.configs.get(css_breakpoint=default_breakpoint)
        section_config.columns = 2
        section_config.gap_choice = "large"
        section_config.save()


class VideoProcessor(WidthModuleProcessorMixin, SimpleModuleProcessor):
    pass


class MultiModuleProcessor(SimpleModuleProcessor):
    """Mark existing items as saved during migration."""

    items_attribute = "items"

    def process(self):
        super().process()
        getattr(self.module, self.items_attribute).all().update(saved=True)


class GalleryProcessor(BreakpointColumnsMixin, MultiModuleProcessor):
    GAP_TRANS = {True: "", False: "small"}
    CROP_TRANS = {True: "3/2", False: ""}

    def process(self):
        super().process()
        section = self.module.section
        section.max_width_choice = self.WIDTH_TRANS[self.old_content.width]
        section.save()

        self.module.crop = self.CROP_TRANS[self.old_content.crop_old]
        self.module.save()

        gap_choice = self.GAP_TRANS[self.old_content.divided]
        columns_by_breakpoint = self._get_columns_by_breakpoint(
            self.old_content.columns
        )
        GalleryConfig = self.apps.get_model("xprez", "GalleryConfig")

        if self.old_content.divided:
            section_config = section.configs.get(css_breakpoint=0)
            section_config.padding_left_choice = ""
            section_config.padding_right_choice = ""
            section_config.save()

        config_0 = GalleryConfig.objects.get(module=self.module, css_breakpoint=0)
        config_0.columns = columns_by_breakpoint.get(0, self.old_content.columns)
        config_0.gap_choice = gap_choice
        config_0.save()

        self._create_breakpoint_configs(config_0, columns_by_breakpoint)

    def _columns_shortcut_choices(self):
        shortcuts = _get_settings("XPREZ_DEFAULTS")["module_shortcuts"]
        return (
            shortcuts.get("xprez.GalleryModule", {})
            .get("columns", {})
            .get("choices", [])
        )

    def get_config_class(self, module):
        return "xprez.GalleryConfig"


class NumbersModuleProcessor(MultiModuleProcessor):
    def get_config_class(self, module):
        return "xprez.NumbersConfig"


class FilesModuleProcessor(MultiModuleProcessor):
    pass


class CodeInputModuleProcessor(SimpleModuleProcessor):
    pass


class CodeTemplateModuleProcessor(SimpleModuleProcessor):
    pass


class ModuleSymlinkProcessor(SimpleModuleProcessor):
    pass


BUILTIN_PROCESSORS = {
    "xprez.CkEditor": CkEditorProcessor,
    "xprez.MediumEditor": MediumEditorProcessor,
    "xprez.GridBoxes": GridboxesProcessor,
    "xprez.QuoteContent": QuotesProcessor,
    "xprez.TextImage": TextImageProcessor,
    "xprez.GalleryModule": GalleryProcessor,
    "xprez.VideoModule": VideoProcessor,
    "xprez.CodeInputModule": CodeInputModuleProcessor,
    "xprez.NumbersModule": NumbersModuleProcessor,
    "xprez.CodeTemplateModule": CodeTemplateModuleProcessor,
    "xprez.FilesModule": FilesModuleProcessor,
    "xprez.ModuleSymlink": ModuleSymlinkProcessor,
}
