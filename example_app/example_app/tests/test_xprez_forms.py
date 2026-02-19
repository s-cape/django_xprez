from django import forms
from django.test import TestCase

from example_app.models import Page
from xprez.admin.forms import DeletableFormMixin, PositionFormMixin, SectionForm
from xprez.models import Section


class DeletableFormMixinTest(TestCase):
    def test_delete_true_clears_errors_and_form_valid(self):
        class Form(DeletableFormMixin, forms.Form):
            required_field = forms.CharField(required=True)

        form = Form(data={"delete": True, "required_field": ""})
        form.full_clean()
        self.assertTrue(form.is_valid())
        self.assertEqual(form._errors, {})


class PositionFormMixinTest(TestCase):
    def test_get_position_from_instance(self):
        page = Page.objects.create(title="P", slug="p")
        section = Section.objects.create(container=page, position=3, saved=True)
        form = SectionForm(instance=section, prefix="section-0")
        self.assertEqual(form.get_position(), 3)

    def test_get_position_from_data(self):
        page = Page.objects.create(title="P", slug="p")
        section = Section.objects.create(container=page, position=0, saved=True)
        form = SectionForm(
            instance=section,
            prefix="section-0",
            data={"section-0-position": "7"},
        )
        self.assertEqual(form.get_position(), 7)
