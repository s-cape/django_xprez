import json
import sys
from unittest import skipIf, skipUnless

from django.apps import apps
from django.contrib import admin
from django.contrib.auth.models import Permission, User
from django.test import SimpleTestCase, TestCase

from xprez import models as xprez_models
from xprez.admin import XprezAdmin

from example_app.models import Page

MCP_INSTALLED = apps.is_installed("xprez_mcp")


@skipIf(MCP_INSTALLED, "runs without django-xprez-mcp")
class WithoutMcpTest(SimpleTestCase):
    def test_nothing_imported(self):
        self.assertNotIn("xprez.mcp", sys.modules)
        self.assertNotIn("xprez.contrib.xprez_mcp.provider", sys.modules)


def build_page(title, slug):
    page = Page.objects.create(title=title, slug=slug)
    section = xprez_models.Section(container=page, saved=True)
    section.save()
    text = xprez_models.TextModule.build()
    text.section = section
    text.saved = True
    text.text = "<h2>Hello</h2><p>World</p>"
    text.save()
    return page, section, text


class McpTestCase(TestCase):
    url = "/mcp/"

    @classmethod
    def setUpTestData(cls):
        cls.root = User.objects.create_superuser("root")
        cls.viewer = User.objects.create_user("viewer", is_staff=True)
        cls.viewer.user_permissions.add(Permission.objects.get(codename="view_page"))
        cls.stranger = User.objects.create_user("stranger", is_staff=True)
        cls.page, cls.section, cls.text = build_page("About", "about")
        cls.gallery = xprez_models.GalleryModule.build()
        cls.gallery.section = cls.section
        cls.gallery.saved = True
        cls.gallery.position = 1
        cls.gallery.save()
        xprez_models.GalleryItem.objects.create(
            module=cls.gallery, file="gallery/office.jpg", alt_text="Office", saved=True
        )
        cls.other, cls.other_section, _text = build_page("Contact", "contact")
        xprez_models.SectionSymlink.objects.create(
            container=cls.other, symlink=cls.section, saved=True, position=1
        )

    def rpc(self, method, params=None, user=None):
        self.client.force_login(user or self.root)
        response = self.client.post(
            self.url,
            json.dumps(
                {"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}}
            ),
            content_type="application/json",
        )
        return response

    def tools(self, user=None):
        result = self.rpc("tools/list", user=user).json()["result"]
        return {tool["name"]: tool for tool in result["tools"]}

    def call(self, name, arguments=None, user=None):
        response = self.rpc(
            "tools/call", {"name": name, "arguments": arguments or {}}, user=user
        )
        return response.json()["result"]

    def data(self, name, arguments=None, user=None):
        result = self.call(name, arguments, user)
        self.assertFalse(result.get("isError"), result)
        if "structuredContent" in result:
            return result["structuredContent"]
        return result["content"][0]["text"]

    def error(self, name, arguments=None, user=None):
        result = self.call(name, arguments, user)
        self.assertTrue(result.get("isError"), result)
        return result["content"][0]["text"]


@skipUnless(MCP_INSTALLED, "needs django-xprez-mcp")
class AccessTest(McpTestCase):
    def test_read_tools(self):
        self.assertEqual(
            set(self.tools(self.viewer)),
            {
                "xprez_guide",
                "xprez_containers_list",
                "xprez_container_get",
                "xprez_module_get",
                "xprez_module_types",
            },
        )

    def test_staff_without_permissions_sees_nothing(self):
        self.assertEqual(set(self.tools(self.stranger)), set())

    def test_scoped_by_xprez_get_container_qs(self):
        from xprez_mcp import MCPServer
        from xprez_mcp.core.context import CallContext

        from xprez.contrib.xprez_mcp.provider import XprezProvider

        class OnlyAbout(XprezAdmin):
            def xprez_get_container_qs(self, request):
                return super().xprez_get_container_qs(request).filter(slug="about")

        site = admin.AdminSite(name="scoped")
        site.register(Page, OnlyAbout)
        provider = type("P", (XprezProvider,), {"admin_site": site})(
            MCPServer(name="scoped")
        )
        ctx = CallContext(server=provider.server, user=self.root)
        listed = provider.containers_list(ctx)
        self.assertEqual([row["id"] for row in listed["results"]], [self.page.pk])
        with self.assertRaisesMessage(Exception, "does not exist"):
            provider.container_get(ctx, container=self.other.pk)


@skipUnless(MCP_INSTALLED, "needs django-xprez-mcp")
class ReadToolsTest(McpTestCase):
    def test_containers_list(self):
        data = self.data("xprez_containers_list", {"type": "example_app.page"})
        self.assertEqual(data["count"], 2)
        self.assertEqual(
            data["results"][0],
            {
                "id": self.other.pk,
                "type": "example_app.page",
                "display": "Contact",
                "admin_url": f"/admin/example_app/page/{self.other.pk}/change/",
                "url": "/contact/",
            },
        )

    def test_containers_list_pages(self):
        data = self.data(
            "xprez_containers_list", {"type": "example_app.page", "limit": 1}
        )
        self.assertEqual(len(data["results"]), 1)
        rest = self.data(
            "xprez_containers_list",
            {"type": "example_app.page", "cursor": data["next_cursor"]},
        )
        self.assertEqual([row["id"] for row in rest["results"]], [self.page.pk])
        self.assertIsNone(rest["next_cursor"])

    def test_containers_list_invalid_type(self):
        self.assertIn(
            "must be one of", self.error("xprez_containers_list", {"type": "x.y"})
        )

    def test_container_get(self):
        data = self.data("xprez_container_get", {"container": self.page.pk})
        self.assertEqual(data["display"], "About")
        self.assertEqual(data["breakpoints"]["0"], "Base style (all sizes < ∞)")
        [section] = data["sections"]
        self.assertEqual(section["kind"], "section")
        self.assertEqual(section["linked_from"], [self.other.pk])
        self.assertEqual(
            [(m["type"], m["id"]) for m in section["modules"]],
            [("text", self.text.pk), ("gallery", self.gallery.pk)],
        )
        self.assertEqual(section["modules"][0]["preview"], "HelloWorld")
        self.assertEqual(section["configs"], {"0": {}})  # defaults left out

    def test_container_get_symlink(self):
        data = self.data("xprez_container_get", {"container": self.other.pk})
        link = data["sections"][1]
        self.assertEqual(link["kind"], "section_symlink")
        self.assertEqual(
            link["links_to"], {"section": self.section.pk, "container": self.page.pk}
        )

    def test_container_get_missing(self):
        self.assertIn(
            "does not exist", self.error("xprez_container_get", {"container": 999999})
        )

    def test_module_get(self):
        data = self.data("xprez_module_get", {"module": self.text.pk})
        self.assertEqual(data["type"], "text")
        self.assertEqual(data["fields"]["text"], "<h2>Hello</h2><p>World</p>")
        self.assertIn("text_align", data["configs"]["0"])
        self.assertNotIn("live_sync", data["fields"])

    def test_module_get_items(self):
        data = self.data("xprez_module_get", {"module": self.gallery.pk})
        [item] = data["items"]
        self.assertEqual(item["alt_text"], "Office")
        self.assertEqual(item["file"]["path"], "gallery/office.jpg")

    def test_module_types(self):
        data = self.data("xprez_module_types", {"container": self.page.pk})
        types = {row["type"]: row for row in data["types"]}
        self.assertIn("text", types)
        self.assertTrue(types["gallery"]["has_items"])
        self.assertNotIn("symlink", types)  # not in the add menu

    def test_module_type_schema(self):
        data = self.data(
            "xprez_module_types", {"container": self.page.pk, "type": "text"}
        )
        self.assertEqual(data["fields"]["text"]["format"], "html")
        html = data["fields"]["text"]["html"]  # from the editor's config
        self.assertIn("h2", html["tags"])
        self.assertNotIn("img", html["tags"])  # no upload over MCP
        self.assertEqual(html["classes"]["a"], ["btn", "btn-primary", "btn-secondary"])
        self.assertNotIn("position", data["fields"])
        self.assertNotIn("section", data["fields"])
        self.assertEqual(data["fields"]["media"]["type"], "file")
        self.assertIn("text_align", data["config_fields"])
        gallery = self.data(
            "xprez_module_types", {"container": self.page.pk, "type": "gallery"}
        )
        self.assertIn("alt_text", gallery["item_fields"])

    def test_guide(self):
        index = self.data("xprez_guide")
        self.assertIn("# Editing content with xprez", index)
        self.assertIn("`layout`", index)
        layout = self.data("xprez_guide", {"topic": "layout"})
        self.assertIn("Mobile (< 500px)", layout)
        modules = self.data("xprez_guide", {"topic": "modules"})
        self.assertIn("`text` (Text): Rich text", modules)


@skipUnless(MCP_INSTALLED, "needs django-xprez-mcp")
class ResourcesTest(McpTestCase):
    def read(self, uri, user=None):
        return self.rpc("resources/read", {"uri": uri}, user=user).json()

    def test_guide_topic(self):
        result = self.read("xprez://guide/text")["result"]
        self.assertIn("`blockquote`", result["contents"][0]["text"])

    def test_container_html(self):
        page, _section, _text = build_page("Plain", "plain")
        result = self.read(f"xprez://containers/{page.pk}")["result"]
        html = result["contents"][0]["text"]
        self.assertIn("<h2>Hello</h2>", html)


@skipUnless(MCP_INSTALLED, "needs django-xprez-mcp")
class WriteAccessTest(McpTestCase):
    def test_root_has_write_tools(self):
        self.assertIn("xprez_module_update", self.tools())
        self.assertEqual(len(self.tools()), 13)

    def test_write_tools_hidden_from_viewer(self):
        response = self.rpc(
            "tools/call",
            {"name": "xprez_module_delete", "arguments": {"module": self.text.pk}},
            user=self.viewer,
        ).json()
        self.assertIn("error", response)
        self.assertTrue(xprez_models.Module.objects.filter(pk=self.text.pk).exists())


@skipUnless(MCP_INSTALLED, "needs django-xprez-mcp")
class ModuleWriteTest(McpTestCase):
    def positions(self, section):
        return list(
            xprez_models.Module.objects.filter(section=section)
            .order_by("position")
            .values_list("pk", "position")
        )

    def test_update(self):
        self.text.css_class = "intro"
        self.text.save()
        data = self.data(
            "xprez_module_update",
            {
                "module": self.text.pk,
                "fields": {"text": "<p>New</p>"},
                "configs": {"0": {"text_align": "center"}},
            },
        )
        self.assertEqual(data["fields"]["text"], "<p>New</p>")
        self.assertEqual(data["fields"]["css_class"], "intro")  # kept
        self.assertEqual(data["configs"]["0"]["text_align"], "center")
        self.text.refresh_from_db()
        self.assertEqual(self.text.text, "<p>New</p>")
        from django.contrib.admin.models import LogEntry

        entry = LogEntry.objects.get(object_id=str(self.page.pk))
        self.assertIn("(MCP)", entry.get_change_message())

    def test_update_breakpoint_config(self):
        self.data(
            "xprez_module_update",
            {"module": self.text.pk, "configs": {"5": {"colspan": 2}}},
        )
        self.assertEqual(self.text.get_configs().get(css_breakpoint=5).colspan, 2)
        self.data(
            "xprez_module_update", {"module": self.text.pk, "configs": {"5": None}}
        )
        self.assertFalse(self.text.get_configs().filter(css_breakpoint=5).exists())

    def test_update_errors(self):
        message = self.error(
            "xprez_module_update",
            {"module": self.text.pk, "fields": {"nope": 1}},
        )
        self.assertIn("unknown nope; valid:", message)
        message = self.error(
            "xprez_module_update",
            {"module": self.text.pk, "configs": {"0": {"text_align": "diagonal"}}},
        )
        self.assertIn("configs.0.text_align", message)
        message = self.error(
            "xprez_module_update", {"module": self.text.pk, "configs": {"0": None}}
        )
        self.assertIn("cannot be removed", message)
        message = self.error(
            "xprez_module_update",
            {"module": self.text.pk, "fields": {"media": {"path": "images/a.jpg"}}},
        )
        self.assertIn("cannot be set over MCP yet", message)

    def test_add_to_section(self):
        data = self.data(
            "xprez_module_add",
            {
                "type": "text",
                "section": self.section.pk,
                "position": 0,
                "fields": {"text": "<p>First</p>"},
            },
        )
        module = xprez_models.Module.objects.get(pk=data["id"])
        self.assertTrue(module.saved)
        self.assertTrue(module.get_configs().get(css_breakpoint=0).saved)
        self.assertEqual(
            self.positions(self.section),
            [(module.pk, 0), (self.text.pk, 1), (self.gallery.pk, 2)],
        )

    def test_add_new_section(self):
        data = self.data(
            "xprez_module_add",
            {
                "type": "quote",
                "container": self.page.pk,
                "position": 0,
                "fields": {"name": "Anna", "quote": "Hello"},
            },
        )
        section = xprez_models.Section.objects.get(pk=data["section"])
        self.assertTrue(section.saved)
        self.assertEqual(section.position, 0)
        self.section.refresh_from_db()
        self.assertEqual(self.section.position, 1)

    def test_add_invalid_rolls_back(self):
        count = xprez_models.Module.objects.count()
        message = self.error(
            "xprez_module_add", {"type": "quote", "section": self.section.pk}
        )
        self.assertIn("quote:", message)
        self.assertEqual(xprez_models.Module.objects.count(), count)

    def test_add_unknown_type(self):
        message = self.error(
            "xprez_module_add", {"type": "symlink", "section": self.section.pk}
        )
        self.assertIn("type must be one of", message)

    def test_move_within_section(self):
        self.data("xprez_module_move", {"module": self.gallery.pk, "position": 0})
        self.assertEqual(
            self.positions(self.section), [(self.gallery.pk, 0), (self.text.pk, 1)]
        )

    def test_move_to_other_section(self):
        target = xprez_models.Section(container=self.page, saved=True, position=1)
        target.save()
        self.data("xprez_module_move", {"module": self.text.pk, "section": target.pk})
        self.assertEqual(self.positions(target), [(self.text.pk, 0)])
        self.assertEqual(self.positions(self.section), [(self.gallery.pk, 0)])

    def test_move_to_other_container(self):
        message = self.error(
            "xprez_module_move",
            {"module": self.text.pk, "section": self.other_section.pk},
        )
        self.assertIn("must be in the module's container", message)

    def test_delete(self):
        self.data("xprez_module_delete", {"module": self.text.pk})
        self.assertFalse(xprez_models.Module.objects.filter(pk=self.text.pk).exists())
        self.assertEqual(self.positions(self.section), [(self.gallery.pk, 0)])


@skipUnless(MCP_INSTALLED, "needs django-xprez-mcp")
class SectionWriteTest(McpTestCase):
    def test_add(self):
        data = self.data(
            "xprez_section_add",
            {
                "container": self.page.pk,
                "position": 0,
                "configs": {"0": {"columns": 3}, "5": {"columns": 1}},
            },
        )
        section = xprez_models.Section.objects.get(pk=data["id"])
        self.assertTrue(section.saved)
        self.assertEqual(section.position, 0)
        self.assertEqual(data["configs"]["0"]["columns"], 3)
        self.assertEqual(data["configs"]["5"]["columns"], 1)

    def test_update_keeps_modules(self):
        self.data(
            "xprez_section_update",
            {"section": self.section.pk, "fields": {"background_color": "#eee"}},
        )
        self.section.refresh_from_db()
        self.assertEqual(self.section.background_color, "#eee")
        self.text.refresh_from_db()
        self.assertEqual(self.text.text, "<h2>Hello</h2><p>World</p>")

    def test_move_link(self):
        link = xprez_models.SectionSymlink.objects.get(container=self.other)
        self.data(
            "xprez_section_move",
            {"section": link.pk, "kind": "section_symlink", "position": 0},
        )
        link.refresh_from_db()
        self.assertEqual(link.position, 0)
        self.other_section.refresh_from_db()
        self.assertEqual(self.other_section.position, 1)

    def test_delete(self):
        self.data("xprez_section_delete", {"section": self.section.pk})
        self.assertFalse(xprez_models.Module.objects.filter(pk=self.text.pk).exists())
