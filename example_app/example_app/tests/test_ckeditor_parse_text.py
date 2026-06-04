from django.test import TestCase

from example_app.models import Page
from xprez.ck_editor import parse_text as ckeditor_parse_text
from xprez.models import Section, TextModule


class CkEditorParseTextSecurityTest(TestCase):
    def test_user_template_tags_are_escaped(self):
        parsed = ckeditor_parse_text.parse_text("<p>{% debug %} {{ secret }}</p>")
        self.assertIn("&#123;% debug %}", parsed)
        self.assertIn("&#123;&#123; secret }}", parsed)
        self.assertNotIn("{% debug %}", parsed)

    def test_render_text_parsed_does_not_execute_user_template_tags(self):
        page = Page.objects.create(title="P", slug="p")
        section = Section.objects.create(container=page, saved=True)
        module = TextModule.objects.create(
            section=section,
            text="<p>{% debug %} {{ leaked }}</p>",
            position=0,
            saved=True,
        )
        parsed = ckeditor_parse_text.parse_text(module.text)
        rendered = ckeditor_parse_text.render_text_parsed(
            parsed,
            extra_context={"module": module, "leaked": "SHOULD_NOT_APPEAR"},
        )
        # Braces are emitted as the HTML entity &#123; — not executed as template syntax
        self.assertIn("&#123;% debug %}", rendered)
        self.assertNotIn("SHOULD_NOT_APPEAR", rendered)

    def test_literal_brace_in_text_is_preserved(self):
        parsed = ckeditor_parse_text.parse_text("<p>Price is {10}</p>")
        rendered = ckeditor_parse_text.render_text_parsed(parsed)
        # &#123; renders as "{" in the browser; the raw HTML contains the entity
        self.assertIn("&#123;10}", rendered)


class CkEditorParseTextImageTest(TestCase):
    def test_inline_image_is_replaced_with_ckeditor_image_tag(self):
        html = (
            '<figure class="image">'
            '<img src="/media/test.jpg" alt="Alt">'
            "<figcaption>Cap</figcaption>"
            "</figure>"
        )
        parsed = ckeditor_parse_text.parse_text(html)
        self.assertIn('{% ckeditor_image "/media/test.jpg" "center"', parsed)
