"""
Custom migration operations and processor bases for the 0.3.0 refactor.

Operations handle inheritance changes that Django automatic migrations can't.
Processor bases provide the framework for migrating old Content models to new
Module models; user code can subclass these for custom module processors.

Reference:
`https://stackoverflow.com/questions/61665607/renaming-a-django-superclass-model-and-updating-the-subclass-pointers-correctly`
"""

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
        """Setup module attributes and create its config."""
        default_breakpoint = _get_settings("XPREZ_DEFAULT_BREAKPOINT")
        xprez_defaults = _get_settings("XPREZ_DEFAULTS")
        config_class = self.apps.get_model(*self.get_config_class(module).split("."))
        default_config = xprez_defaults["module_config"]["default"]
        self.config, _created = config_class.objects.get_or_create(
            module=module,
            css_breakpoint=default_breakpoint,
            defaults={
                "saved": True,
                "vertical_align_grid": default_config["vertical_align_grid"],
                "horizontal_align_grid": default_config["horizontal_align_grid"],
                "vertical_align_flex": default_config["vertical_align_flex"],
                "horizontal_align_flex": default_config["horizontal_align_flex"],
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
        self.delete_processed_module()

    def prepare_new_modules(self):
        raise NotImplementedError()

    def finalize_new_modules(self):
        for new_module in self.new_modules:
            new_module.content_type = _content_type(new_module)
            new_module.section = self.module_base.section
            new_module.saved = True
            new_module.created = timezone.now()
            new_module.changed = timezone.now()
            new_module.save()
            self.finalize(new_module)

    def delete_processed_module(self):
        self.module_base.delete()


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
    default_breakpoint = _get_settings("XPREZ_DEFAULT_BREAKPOINT")
    xprez_defaults = _get_settings("XPREZ_DEFAULTS")
    ContentsContainer = apps.get_model("xprez", "ContentsContainer")
    Content = apps.get_model("xprez", "Content")

    Container = apps.get_model("xprez", "Container")
    Module = apps.get_model("xprez", "Module")
    Section = apps.get_model("xprez", "Section")

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
                alternate_background=old_content.alternate_color,
                background_color=old_content.background_color,
                css_class=old_content.css_class,
                saved=True,
            )
            section_config, _created = section.configs.get_or_create(
                css_breakpoint=default_breakpoint,
                defaults={
                    "saved": True,
                    "vertical_align_grid": xprez_defaults["section_config"][
                        "vertical_align_grid"
                    ],
                    "horizontal_align_grid": xprez_defaults["section_config"][
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


class TextModuleProcessorBase(ModuleReplaceProcessor):
    def get_config_class(self, module):
        return "xprez.TextConfig"

    def prepare_new_modules(self, **kwargs):
        TextModule = self.apps.get_model("xprez", "TextModule")
        return [TextModule(text=self.old_content.text)]

    def finalize(self, module):
        super().finalize(module)
        if getattr(self.old_content, "box", False):
            self.config.background = True
            self.config.padding_left_choice = "medium"
            self.config.padding_right_choice = "medium"
            self.config.padding_top_choice = "medium"
            self.config.padding_bottom_choice = "medium"
            self.config.save()


class CkEditorProcessor(TextModuleProcessorBase):
    pass


class MediumEditorProcessor(TextModuleProcessorBase):
    pass


class GridboxesProcessor(TextModuleProcessorBase):
    MARGIN_TRANS = {"none": "", "m": "medium", "l": "large"}
    TEXT_SIZE_TRANS = {"xs": "smallest", "s": "small", "m": "normal"}

    def prepare_new_modules(self):
        TextModule = self.apps.get_model("xprez", "TextModule")
        new_modules = []
        for index, box in enumerate(self.old_content.boxes or []):
            new_modules += [TextModule(position=index, text=box)]
        return new_modules

    def finalize_new_modules(self):
        super().finalize_new_modules()
        section = self.module_base.section
        section.max_width_choice = self.WIDTH_TRANS.get(
            getattr(self.old_content, "width", "full"), "full"
        )
        section.save()

        default_breakpoint = _get_settings("XPREZ_DEFAULT_BREAKPOINT")
        section_config = section.configs.get(css_breakpoint=default_breakpoint)
        section_config.columns = self.old_content.columns
        section_config.gap_choice = self.MARGIN_TRANS.get(
            self.old_content.margin, "medium"
        )
        section_config.save()

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


class QuotesProcessor(ModuleReplaceProcessor):
    def prepare_new_modules(self):
        QuoteModule = self.apps.get_model("xprez", "QuoteModule")
        quotes = self.old_content.quotes.all()
        if not self.old_content.display_two:
            quotes = quotes[:1]

        if len(quotes) > 1:
            default_breakpoint = _get_settings("XPREZ_DEFAULT_BREAKPOINT")
            section_config = self.module_base.section.configs.get_or_create(
                css_breakpoint=default_breakpoint
            )[0]
            section_config.columns = 2
            section_config.save()

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

    def finalize(self, module):
        super().finalize(module)
        if getattr(self.old_content, "box", False):
            self.config.background = True
            self.config.padding_left_choice = "medium"
            self.config.padding_right_choice = "medium"
            self.config.padding_top_choice = "medium"
            self.config.padding_bottom_choice = "medium"
            self.config.save()


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
                module=module, file=self.old_content.image, position=0
            )

    def finalize_new_modules(self):
        super().finalize_new_modules()
        section = self.module_base.section
        default_breakpoint = _get_settings("XPREZ_DEFAULT_BREAKPOINT")
        section_config = section.configs.get(css_breakpoint=default_breakpoint)
        section_config.columns = 2
        section_config.gap_choice = "large"
        section_config.save()


class VideoProcessor(SimpleModuleProcessor):
    def process(self):
        super().process()
        section = self.module.section
        section.max_width_choice = self.WIDTH_TRANS.get(
            getattr(self.old_content, "width", "full"), "full"
        )
        section.save()


class GalleryProcessor(SimpleModuleProcessor):
    GAP_TRANS = {True: "small", False: ""}
    CROP_TRANS = {True: "3/2", False: ""}

    def process(self):
        super().process()
        default_breakpoint = _get_settings("XPREZ_DEFAULT_BREAKPOINT")
        section_config = self.module.section.configs.get(
            css_breakpoint=default_breakpoint
        )
        section_config.max_width_choice = self.WIDTH_TRANS[self.old_content.width]
        section_config.columns = self.old_content.columns
        section_config.gap_choice = self.GAP_TRANS[self.old_content.divided]
        section_config.save()

        self.module.crop = self.CROP_TRANS[self.old_content.crop_old]
        self.module.save()

        self.config.gap_choice = self.GAP_TRANS[self.old_content.divided]
        self.config.save()

    def get_config_class(self, module):
        return "xprez.GalleryConfig"


class DownloadModuleProcessor(SimpleModuleProcessor):
    pass


class ModuleSymlinkProcessor(SimpleModuleProcessor):
    def process(self):
        super().process()
        print("TODO: process module symlink")


BUILTIN_PROCESSORS = {
    "xprez.CkEditor": CkEditorProcessor,
    "xprez.MediumEditor": MediumEditorProcessor,
    "xprez.GridBoxes": GridboxesProcessor,
    "xprez.QuoteContent": QuotesProcessor,
    "xprez.TextImage": TextImageProcessor,
    "xprez.GalleryModule": GalleryProcessor,
    "xprez.VideoModule": VideoProcessor,
    "xprez.CodeInputModule": SimpleModuleProcessor,
    "xprez.NumbersModule": SimpleModuleProcessor,
    "xprez.CodeTemplateModule": SimpleModuleProcessor,
    "xprez.FilesModule": DownloadModuleProcessor,
    "xprez.ModuleSymlink": ModuleSymlinkProcessor,
}
