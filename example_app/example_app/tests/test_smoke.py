from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from example_app.models import Page
from xprez.models import Section, TextModule


class SmokeTest(TestCase):
    def test_smoke(self):
        User = get_user_model()
        User.objects.create_user(
            username="test", password="test", is_staff=True, is_superuser=True
        )

        page = Page.objects.create(title="Test Page", slug="test-page")
        section = Section.objects.create(container=page, saved=True)
        TextModule.objects.create(
            section=section, text="<p>Test Module</p>", position=0, saved=True
        )

        response = self.client.get(page.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        self.client.login(username="test", password="test")
        response = self.client.get(
            reverse("admin:example_app_page_change", args=[page.pk])
        )
        self.assertEqual(response.status_code, 200)
