from django.test import RequestFactory, TestCase

from example_app.models import Page
from xprez.models.modules import CLIPBOARD_TEXT_MAX_LENGTH
from xprez.models import Section, TextModule


class TextModuleSaveTest(TestCase):
    def test_save_sets_content_type_and_polymorph(self):
        page = Page.objects.create(title="P", slug="p")
        section = Section.objects.create(container=page, saved=True)
        module = TextModule.objects.create(
            section=section, text="<p>Hello</p>", position=0, saved=True
        )
        self.assertEqual(module.content_type, "xprez.TextModule")
        self.assertIs(module.polymorph, module)


class TextModuleRenderFrontTest(TestCase):
    def test_render_front_returns_parsed_text(self):
        page = Page.objects.create(title="P", slug="p")
        section = Section.objects.create(container=page, saved=True)
        module = TextModule.objects.create(
            section=section, text="<p>Hello</p>", position=0, saved=True
        )
        request = RequestFactory().get("/")
        context = {"request": request}
        result = module.render_front(context)
        self.assertIn("Hello", result)


class TextModuleClipboardPreviewTest(TestCase):
    def test_long_text_truncated_with_ellipsis(self):
        page = Page.objects.create(title="P", slug="p")
        section = Section.objects.create(container=page, saved=True)
        long_text = "x" * (CLIPBOARD_TEXT_MAX_LENGTH + 50)
        module = TextModule.objects.create(
            section=section, text=long_text, position=0, saved=True
        )
        preview = module.clipboard_text_preview()
        self.assertLessEqual(len(preview), CLIPBOARD_TEXT_MAX_LENGTH)
        self.assertTrue(preview.endswith("..."))

    def test_short_text_not_truncated(self):
        page = Page.objects.create(title="P", slug="p")
        section = Section.objects.create(container=page, saved=True)
        short_text = "Hi"
        module = TextModule.objects.create(
            section=section, text=short_text, position=0, saved=True
        )
        self.assertEqual(module.clipboard_text_preview(), "Hi")
