import copy

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TestCase

from example_app.models import Page
from xprez.models import Section, TextModule
from xprez.utils import class_content_type, copy_model, import_class


class ClassContentTypeTest(TestCase):
    def test_returns_app_label_and_model_name(self):
        self.assertEqual(class_content_type(TextModule), "xprez.TextModule")


class ImportClassTest(TestCase):
    def test_string_path_returns_class(self):
        result = import_class("xprez.models.TextModule")
        self.assertIs(result, TextModule)

    def test_class_passed_through(self):
        self.assertIs(import_class(TextModule), TextModule)


class CopyModelTest(TestCase):
    def _historical_text_module_class(self):
        """Return the __fake__ TextModule class at the latest migration state."""
        executor = MigrationExecutor(connection)
        state = executor.loader.project_state(executor.loader.graph.leaf_nodes())
        return state.apps.get_model("xprez", "TextModule")

    def test_preserves_class_for_historical_models(self):
        """Regression: copy.copy routes through Model.__reduce__, which fetches
        the class from the live app registry — silently swapping a historical
        __fake__ class for the live one. That leaks any new live fields into
        the copy as "deferred", which makes Model.save auto-set update_fields
        and break multi-table-inherited copies in data migrations with
        "Cannot force an update in save() with no primary key."
        """
        HistoricalTextModule = self._historical_text_module_class()
        self.assertIsNot(HistoricalTextModule, TextModule)

        page = Page.objects.create(title="t", slug="t")
        section = Section.objects.create(container=page, position=0, saved=True)
        historical = HistoricalTextModule.objects.create(
            section_id=section.pk, text="<p>x</p>", position=0, saved=True
        )

        self.assertIsNot(copy.copy(historical).__class__, HistoricalTextModule)
        self.assertIs(copy_model(historical).__class__, HistoricalTextModule)

    def test_returns_unsaved_copy_ready_for_insert(self):
        page = Page.objects.create(title="t", slug="t")
        section = Section.objects.create(container=page, position=0, saved=True)
        original = TextModule.objects.create(
            section=section, text="<p>x</p>", position=0, saved=True
        )

        new = copy_model(original)

        self.assertIsNone(new.pk)
        self.assertIsNone(new.id)
        self.assertTrue(new._state.adding)
        self.assertEqual(new.text, original.text)
