from django.test import TestCase

from xprez.models import TextModule
from xprez.registry import module_registry


class ModuleRegistryTest(TestCase):
    def test_get_returns_registered_module_class(self):
        self.assertIs(module_registry.get("xprez.TextModule"), TextModule)

    def test_register_duplicate_module_key_raises(self):
        class FakeModule:
            module_key = "text"

            @classmethod
            def class_content_type(cls):
                return "test.fakemodule"

        with self.assertRaises(ValueError) as ctx:
            module_registry.register(FakeModule)
        self.assertIn("text", str(ctx.exception))
        self.assertIn("already registered", str(ctx.exception))
