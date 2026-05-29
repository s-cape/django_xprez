from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from example_app.models import Page
from xprez.models import Section, TextModule


def _setup_user_and_login(client):
    User = get_user_model()
    User.objects.create_user(
        username="staff", password="pass", is_staff=True, is_superuser=True
    )
    client.login(username="staff", password="pass")


class AddViewTest(TestCase):
    def setUp(self):
        _setup_user_and_login(self.client)
        self.page = Page.objects.create(title="Test Page", slug="test-page")

    def test_empty_section_creates_section_without_modules(self):
        url = reverse("admin:page_add", args=[self.page.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        section = Section.objects.get(container=self.page)
        self.assertEqual(section.modules.count(), 0)
        self.assertIn(section.instance_key, response.json()[0]["html"])

    def test_section_with_module_creates_both(self):
        url = reverse("admin:page_add", args=[self.page.pk, "xprez.TextModule"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        section = Section.objects.get(container=self.page)
        self.assertEqual(section.modules.count(), 1)
        self.assertIsInstance(section.modules.first().polymorph, TextModule)

    def test_module_in_existing_section_creates_module_only(self):
        section = Section.objects.create(container=self.page, position=0, saved=True)
        url = reverse(
            "admin:page_add", args=[self.page.pk, section.pk, "xprez.TextModule"]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Section.objects.filter(container=self.page).count(), 1)
        self.assertEqual(section.modules.count(), 1)

    def test_unknown_content_type_returns_404(self):
        url = reverse("admin:page_add", args=[self.page.pk, "xprez.NoSuchModule"])
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_unknown_container_returns_404(self):
        url = reverse("admin:page_add", args=[99999])
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_requires_staff(self):
        self.client.logout()
        url = reverse("admin:page_add", args=[self.page.pk])
        self.assertIn(self.client.get(url).status_code, (302, 403))
