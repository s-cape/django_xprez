from django.test import TestCase

from xprez.models import TextModule
from xprez.utils import class_content_type, import_class


class ClassContentTypeTest(TestCase):
    def test_returns_app_label_and_model_name(self):
        self.assertEqual(class_content_type(TextModule), "xprez.TextModule")


class ImportClassTest(TestCase):
    def test_string_path_returns_class(self):
        result = import_class("xprez.models.TextModule")
        self.assertIs(result, TextModule)

    def test_class_passed_through(self):
        self.assertIs(import_class(TextModule), TextModule)
