from django import forms
from django.test import TestCase

from example_app.models import Page
from xprez.admin.fields import AspectRatioFormField
from xprez.admin.forms import DeletableFormMixin, SectionForm
from xprez.models import Section, TextModule


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


class AspectRatioFieldTest(TestCase):
    def test_form_field_normalizes_colons(self):
        field = AspectRatioFormField(required=False)
        self.assertEqual(field.to_python("16:9"), "16/9")
        self.assertEqual(field.to_python("16/9"), "16/9")
        self.assertEqual(field.to_python(""), "")

    def test_model_field_normalizes_on_save(self):
        page = Page.objects.create(title="P", slug="p")
        section = Section.objects.create(container=page, position=0, saved=True)
        module = TextModule.objects.create(
            section=section, text="<p>Hello</p>", position=0, saved=True
        )
        config, _ = module.get_or_create_config(0)

        config.aspect_ratio = "16:9"
        config.save()
        config.refresh_from_db()

        self.assertEqual(config.aspect_ratio, "16/9")
