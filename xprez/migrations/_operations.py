"""
Custom migration operations for inheritance refactors.
Django automatic migrations can't handle this.
Reference:
`https://stackoverflow.com/questions/61665607/renaming-a-django-superclass-model-and-updating-the-subclass-pointers-correctly`
"""

from django.db import models
from django.db.migrations.operations.base import Operation


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
        # if not self.allow_migrate_model(schema_editor.connection.alias, to_model):
        #     return

        renderable_from_state = self._render_as_plain_model(app_label, from_state)
        from_model = renderable_from_state.apps.get_model(app_label, self.model_name)
        from_field = from_model._meta.get_field(self.from_field_name)
        to_field = to_model._meta.get_field(self.to_field_name)
        schema_editor.alter_field(from_model, from_field, to_field)

    # def database_backwards(self, app_label, schema_editor, from_state, to_state):
    #     to_model = to_state.apps.get_model(app_label, self.model_name)
    #     if not self.allow_migrate_model(schema_editor.connection.alias, to_model):
    #         return

    #     renderable_from_state = self._render_as_plain_model(app_label, from_state)
    #     from_model = renderable_from_state.apps.get_model(app_label, self.model_name)
    #     from_field = from_model._meta.get_field(self.to_field_name)
    #     to_field = to_model._meta.get_field(self.from_field_name)
    #     schema_editor.alter_field(from_model, from_field, to_field)

    # def state_backwards(self, app_label, state):
    #     model_name = self.model_name.lower()
    #     state.rename_field(
    #         app_label, model_name, self.to_field_name, self.from_field_name
    #     )
    #     model_state = state.models[app_label, model_name]
    #     model_state.bases = self._replace_base(
    #         model_state.bases,
    #         from_remote_model=self.to_remote_model,
    #         to_remote_model=self.from_remote_model,
    #     )
    #     new_field = model_state.fields[self.from_field_name].clone()
    #     new_field.remote_field.model = self.from_remote_model
    #     new_field.name = self.from_field_name
    #     state.alter_field(
    #         app_label,
    #         model_name,
    #         self.from_field_name,
    #         new_field,
    #         preserve_default=True,
    #     )

    # def describe(self):
    #     return (
    #         f"Rename {self.from_field_name} to {self.to_field_name} on "
    #         f"{self.model_name}"
    #     )


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
