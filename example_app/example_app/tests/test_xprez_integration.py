from django.test import TestCase

from example_app.models import Page
from xprez.models import Section, TextModule


class FrontRenderIntegrationTest(TestCase):
    def test_page_with_section_and_text_module_renders_200(self):
        page = Page.objects.create(title="Test Page", slug="test-page")
        section = Section.objects.create(
            container=page, position=0, saved=True, visible=True
        )
        TextModule.objects.create(
            section=section, text="<p>Content</p>", position=0, saved=True
        )
        response = self.client.get(page.get_absolute_url())
        self.assertEqual(response.status_code, 200)
