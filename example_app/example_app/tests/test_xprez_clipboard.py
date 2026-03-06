import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from example_app.models import Page
from xprez.models import Section, SectionSymlink, TextModule
from xprez.modules.symlink import ModuleSymlink


def _setup_user_and_login(client):
    User = get_user_model()
    user = User.objects.create_user(
        username="staff", password="pass", is_staff=True, is_superuser=True
    )
    client.login(username="staff", password="pass")
    return user


def _setup_page_with_module():
    page = Page.objects.create(title="Test Page", slug="test-page")
    section = Section.objects.create(container=page, position=0, saved=True)
    module = TextModule.objects.create(
        section=section, text="<p>Hello</p>", position=0, saved=True
    )
    return page, section, module


class ClipboardClipViewTest(TestCase):
    def setUp(self):
        _setup_user_and_login(self.client)
        self.page, self.section, self.module = _setup_page_with_module()

    def test_clip_module_stores_in_session(self):
        url = reverse(
            "admin:page_clipboard_clip",
            args=["module", self.module.pk],
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        clipboard = self.client.session["xprez_clipboard"]
        # Django session serializer converts tuples to lists
        self.assertEqual(clipboard, [["module", self.module.pk]])

    def test_clip_section_stores_section_pk_in_session(self):
        url = reverse(
            "admin:page_clipboard_clip",
            args=["section", self.section.pk],
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        clipboard = self.client.session["xprez_clipboard"]
        self.assertEqual(clipboard, [["section", self.section.pk]])

    def test_clip_container_stores_container_pk_in_session(self):
        url = reverse(
            "admin:page_clipboard_clip",
            args=["container", self.page.pk],
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        clipboard = self.client.session["xprez_clipboard"]
        self.assertEqual(clipboard, [["container", self.page.pk]])

    def test_clip_respects_max_length(self):
        for i in range(12):
            url = reverse("admin:page_clipboard_clip", args=["module", self.module.pk])
            self.client.post(url)
        clipboard = self.client.session["xprez_clipboard"]
        self.assertLessEqual(len(clipboard), 10)

    def test_clip_prepends_most_recent(self):
        second_module = TextModule.objects.create(
            section=self.section, text="<p>Second</p>", position=1, saved=True
        )
        self.client.post(
            reverse("admin:page_clipboard_clip", args=["module", self.module.pk])
        )
        self.client.post(
            reverse("admin:page_clipboard_clip", args=["module", second_module.pk])
        )
        clipboard = self.client.session["xprez_clipboard"]
        self.assertEqual(clipboard[0], ["module", second_module.pk])


class ClipboardListViewTest(TestCase):
    def setUp(self):
        _setup_user_and_login(self.client)
        self.page, self.section, self.module = _setup_page_with_module()

    def _list_url(self, section=None):
        if section is not None:
            return reverse(
                "admin:page_clipboard_list",
                args=[self.page.pk, section.pk],
            )
        return reverse("admin:page_clipboard_list", args=[self.page.pk])

    def test_list_empty_when_no_clipboard(self):
        response = self.client.get(self._list_url(self.section))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "clipboard empty")

    def test_list_empty_container_level(self):
        response = self.client.get(self._list_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "clipboard empty")

    def test_list_shows_module_when_in_clipboard(self):
        session = self.client.session
        session["xprez_clipboard"] = [("module", self.module.pk)]
        session.save()
        response = self.client.get(self._list_url(self.section))
        self.assertEqual(response.status_code, 200)
        # empty-message element is always in DOM; data-hidden hides it when non-empty
        self.assertContains(response, "data-hidden\n    >clipboard empty")
        self.assertContains(response, 'data-component="xprez-clipboard-paste"')

    def test_list_shows_section_when_in_clipboard(self):
        session = self.client.session
        session["xprez_clipboard"] = [("section", self.section.pk)]
        session.save()
        # section items can only be pasted at container level (no target_section)
        response = self.client.get(self._list_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "data-hidden\n    >clipboard empty")
        self.assertContains(response, 'data-component="xprez-clipboard-paste"')

    def test_list_shows_container_when_in_clipboard(self):
        session = self.client.session
        session["xprez_clipboard"] = [("container", self.page.pk)]
        session.save()
        # container items can only be pasted at container level (no target_section)
        response = self.client.get(self._list_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "data-hidden\n    >clipboard empty")
        self.assertContains(response, 'data-component="xprez-clipboard-paste"')

    def test_list_container_level_shows_container_paste_button(self):
        session = self.client.session
        session["xprez_clipboard"] = [("container", self.page.pk)]
        session.save()
        response = self.client.get(self._list_url())
        self.assertContains(response, "data-hidden\n    >clipboard empty")
        self.assertContains(response, 'data-component="xprez-clipboard-paste"')

    def test_list_container_level_module_shows_paste_button(self):
        session = self.client.session
        session["xprez_clipboard"] = [("module", self.module.pk)]
        session.save()
        response = self.client.get(self._list_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "data-hidden\n    >clipboard empty")
        self.assertContains(response, 'data-component="xprez-clipboard-paste"')

    def test_list_shows_unavailable_when_module_not_in_available_modules(self):
        from unittest.mock import patch

        session = self.client.session
        session["xprez_clipboard"] = [("module", self.module.pk)]
        session.save()
        with patch("xprez.conf.settings.XPREZ_MODULES_ALLOWED", []):
            response = self.client.get(self._list_url(self.section))
            self.assertContains(response, "data-disabled")

    def test_list_ignores_deleted_objects(self):
        session = self.client.session
        session["xprez_clipboard"] = [("module", 99999)]
        session.save()
        response = self.client.get(self._list_url(self.section))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "clipboard empty")


class ClipboardPasteViewTest(TestCase):
    def setUp(self):
        _setup_user_and_login(self.client)
        self.page, self.section, self.module = _setup_page_with_module()

    def _paste_url(self, key, pk, action, section=None):
        args = [key, pk, action, self.page.pk]
        if section is not None:
            args += [section.pk]
        return reverse("admin:page_clipboard_paste", args=args)

    def test_paste_module_creates_copy_in_section(self):
        url = self._paste_url("module", self.module.pk, "duplicate", self.section)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertIn("html", data[0])
        new_module = TextModule.objects.exclude(pk=self.module.pk).get(
            section=self.section
        )
        self.assertNotEqual(new_module.pk, self.module.pk)

    def test_paste_module_returns_html_template(self):
        url = self._paste_url("module", self.module.pk, "duplicate", self.section)
        response = self.client.post(url)
        data = json.loads(response.content)
        self.assertIn("<div", data[0]["html"])

    def test_paste_section_copies_all_modules_at_container_level(self):
        TextModule.objects.create(
            section=self.section, text="<p>Second</p>", position=1, saved=True
        )
        url = reverse(
            "admin:page_clipboard_paste",
            args=["section", self.section.pk, "duplicate", self.page.pk],
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(self.page.sections.count(), 2)
        new_section = self.page.sections.exclude(pk=self.section.pk).get()
        self.assertEqual(new_section.modules.count(), 2)

    def test_paste_section_symlink_at_container_level_creates_section_symlink(self):
        url = reverse(
            "admin:page_clipboard_paste",
            args=["section", self.section.pk, "symlink", self.page.pk],
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertIn("html", data[0])
        symlink = SectionSymlink.objects.get(container=self.page)
        self.assertEqual(symlink.symlink_id, self.section.pk)

    def test_paste_section_with_target_section_returns_400(self):
        target_section = Section.objects.create(
            container=self.page, position=1, saved=True
        )
        url = reverse(
            "admin:page_clipboard_paste",
            args=[
                "section",
                self.section.pk,
                "duplicate",
                self.page.pk,
                target_section.pk,
            ],
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 400)

    def test_paste_container_copies_all_sections(self):
        second_section = Section.objects.create(
            container=self.page, position=1, saved=True
        )
        TextModule.objects.create(
            section=second_section, text="<p>Other</p>", position=0, saved=True
        )
        target_page = Page.objects.create(title="Target", slug="target")
        target_section = Section.objects.create(
            container=target_page, position=0, saved=True
        )
        url = reverse(
            "admin:page_clipboard_paste",
            args=["container", self.page.pk, "duplicate", target_page.pk],
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 2)
        self.assertEqual(target_page.sections.count(), 3)  # original + 2 pasted

    def test_paste_container_symlink_creates_section_symlinks(self):
        target_page = Page.objects.create(title="Target2", slug="target2")
        url = reverse(
            "admin:page_clipboard_paste",
            args=["container", self.page.pk, "symlink", target_page.pk],
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        symlink = SectionSymlink.objects.get(container=target_page)
        self.assertEqual(symlink.symlink_id, self.section.pk)

    def test_paste_container_with_target_section_returns_400(self):
        target_page = Page.objects.create(title="Target3", slug="target3")
        target_section = Section.objects.create(
            container=target_page, position=0, saved=True
        )
        url = reverse(
            "admin:page_clipboard_paste",
            args=[
                "container",
                self.page.pk,
                "duplicate",
                target_page.pk,
                target_section.pk,
            ],
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 400)

    def test_paste_symlink_action_creates_module_symlink(self):
        url = self._paste_url("module", self.module.pk, "symlink", self.section)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        symlink = ModuleSymlink.objects.get(section=self.section)
        self.assertEqual(symlink.symlink_id, self.module.pk)

    def test_paste_unavailable_module_returns_400(self):
        from unittest.mock import patch

        with patch("xprez.conf.settings.XPREZ_MODULES_ALLOWED", []):
            url = self._paste_url("module", self.module.pk, "duplicate", self.section)
            response = self.client.post(url)
            self.assertEqual(response.status_code, 400)


class ModuleSymlinkCreateTest(TestCase):
    def setUp(self):
        self.page, self.section, self.module = _setup_page_with_module()

    def test_creates_symlink_in_section(self):
        symlink = ModuleSymlink.objects.create(
            section=self.section, symlink=self.module
        )
        self.assertEqual(symlink.section, self.section)
        self.assertEqual(symlink.symlink, self.module)
        self.assertTrue(ModuleSymlink.objects.filter(pk=symlink.pk).exists())

    def test_default_position_is_zero(self):
        symlink = ModuleSymlink.objects.create(
            section=self.section, symlink=self.module
        )
        self.assertEqual(symlink.position, 0)


class ModuleCopyToTest(TestCase):
    def setUp(self):
        self.page, self.section, self.module = _setup_page_with_module()

    def test_duplicate_to_same_section(self):
        new_module = self.module.duplicate_to(self.section)
        self.assertEqual(new_module.section, self.section)
        self.assertNotEqual(new_module.pk, self.module.pk)

    def test_duplicate_to_different_section(self):
        target_section = Section.objects.create(
            container=self.page, position=1, saved=True
        )
        new_module = self.module.duplicate_to(target_section)
        self.assertEqual(new_module.section, target_section)


class ContainerCopyToTest(TestCase):
    def setUp(self):
        self.page, self.section, self.module = _setup_page_with_module()

    def test_duplicate_to_creates_section_and_modules_in_target(self):
        target_page = Page.objects.create(title="Target", slug="target")
        self.page.duplicate_to(target_page)
        self.assertEqual(target_page.sections.count(), 1)
        target_section = target_page.sections.first()
        self.assertEqual(target_section.modules.count(), 1)
        new_module = target_section.modules.first().polymorph
        self.assertIsInstance(new_module, TextModule)
        self.assertNotEqual(new_module.pk, self.module.pk)
