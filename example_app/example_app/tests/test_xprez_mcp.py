import base64
import io
import json
import shutil
import sys
import tempfile
from pathlib import Path
from unittest import skipIf, skipUnless

from django.apps import apps
from django.contrib import admin
from django.contrib.auth.models import Permission, User
from django.test import SimpleTestCase, TestCase, override_settings

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
        media = data["fields"]["media"]["anyOf"]  # django-xprez-mcp's file argument
        self.assertEqual(media[0]["required"], ["data", "name"])
        self.assertEqual(data["config_fields"]["text_align"]["enum"][0], "left")
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
        self.assertEqual(len(self.tools()), 17)

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
        self.assertIn("fields.media: path is not accepted here", message)

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


@skipUnless(MCP_INSTALLED, "needs django-xprez-mcp")
class OwnRulesTest(McpTestCase):
    """A provider with its own permissions and no ModelAdmin."""

    def provider(self):
        from xprez_mcp import MCPServer

        from xprez.admin import XprezAdminMixin
        from xprez.contrib.xprez_mcp.provider import XprezProvider

        class PageXprez(XprezAdminMixin):
            model = Page

            def xprez_allowed_modules(self, container=None):
                return ["xprez.TextModule"]

        class OwnRules(XprezProvider):
            def get_container_models(self, ctx):
                return {Page: PageXprez()}

            def get_container_queryset(self, ctx, model, xprez_admin, write=False):
                return Page.objects.filter(slug="about")

            def has_container_permission(
                self, ctx, model, xprez_admin, container=None, write=False
            ):
                return ctx.user.username == "editor" if write else True

        return OwnRules(MCPServer(name="own-rules"))

    def ctx(self, provider, username):
        from xprez_mcp.core.context import CallContext

        user = User.objects.create_user(username)  # not staff
        return CallContext(server=provider.server, user=user)

    def test_reads_without_admin(self):
        provider = self.provider()
        ctx = self.ctx(provider, "reader")
        self.assertTrue(provider.has_permission(ctx))
        self.assertFalse(provider.can_write(ctx))
        listed = provider.containers_list(ctx)
        self.assertEqual([row["id"] for row in listed["results"]], [self.page.pk])
        self.assertIsNone(listed["results"][0]["admin_url"])
        with self.assertRaisesMessage(Exception, "does not exist"):
            provider.container_get(ctx, container=self.other.pk)
        types = provider.module_types(ctx, container=self.page.pk)["types"]
        self.assertEqual([row["type"] for row in types], ["text"])

    def test_writes_with_own_permission(self):
        provider = self.provider()
        with self.assertRaisesMessage(Exception, "cannot change"):
            provider.module_update(
                self.ctx(provider, "reader"),
                module=self.text.pk,
                fields={"text": "<p>No</p>"},
            )
        ctx = self.ctx(provider, "editor")
        self.assertTrue(provider.can_write(ctx))
        provider.module_update(ctx, module=self.text.pk, fields={"text": "<p>Yes</p>"})
        self.text.refresh_from_db()
        self.assertEqual(self.text.text, "<p>Yes</p>")
        from django.contrib.admin.models import LogEntry

        self.assertFalse(LogEntry.objects.exists())  # no ModelAdmin, no history


class CleanHtmlTest(SimpleTestCase):
    """The cleaner needs no django-xprez-mcp."""

    def clean(self, html):
        from xprez.contrib.xprez_mcp.html import clean_html, module_text_rules

        return clean_html(html, module_text_rules())

    def test_allowed_kept(self):
        html = (
            '<h2>A</h2><p><strong>b</strong> <a href="/c/">c</a></p><ul><li>d</li></ul>'
        )
        self.assertEqual(self.clean(html), (html, []))

    def test_unknown_tags_unwrapped(self):
        self.assertEqual(
            self.clean('<p>a <span style="x">b</span></p>'),
            ("<p>a b</p>", ["removed tags: span"]),
        )

    def test_dangerous_content_dropped(self):
        html, notes = self.clean(
            "<script>alert(1)</script><p>a</p><style>p{}</style><!-- c -->"
        )
        self.assertEqual(html, "<p>a</p>")
        self.assertEqual(notes, ["removed tags: script, style"])

    def test_attributes(self):
        html, _notes = self.clean(
            '<p onclick="x()"><a href="/a/" class="btn btn-primary evil" '
            'target="_top" rel="x">a</a></p>'
        )
        self.assertEqual(html, '<p><a class="btn btn-primary" href="/a/">a</a></p>')

    def test_unsafe_urls(self):
        for url in ("javascript:alert(1)", " JaVa\tscript:x", "data:text/html,x"):
            html, _notes = self.clean(f'<p><a href="{url}">a</a></p>')
            self.assertEqual(html, "<p><a>a</a></p>", url)
        for url in ("https://example.com/", "/contact/", "#top", "mailto:a@b.cz"):
            html, _notes = self.clean(f'<p><a href="{url}">a</a></p>')
            self.assertIn(f'href="{url}"', html)

    def test_renamed(self):
        html, notes = self.clean("<h1>A</h1><p><b>b</b> <i>i</i></p><h6>c</h6>")
        self.assertEqual(
            html, "<h2>A</h2><p><strong>b</strong> <em>i</em></p><h4>c</h4>"
        )
        self.assertIn("h1 to h2", notes[0])

    def test_top_level_text_wrapped(self):
        self.assertEqual(
            self.clean("a <strong>b</strong><ul><li>c</li></ul>d")[0],
            "<p>a <strong>b</strong></p><ul><li>c</li></ul><p>d</p>",
        )


@skipUnless(MCP_INSTALLED, "needs django-xprez-mcp")
class CleanOnWriteTest(McpTestCase):
    def test_module_update_cleans_text(self):
        data = self.data(
            "xprez_module_update",
            {
                "module": self.text.pk,
                "fields": {"text": "<h1>Title</h1><div>a<script>x</script></div>"},
            },
        )
        self.assertEqual(data["fields"]["text"], "<h2>Title</h2><p>a</p>")
        self.assertEqual(
            data["notes"],
            [
                "fields.text: changed tags: h1 to h2",
                "fields.text: removed tags: div, script",
            ],
        )

    def test_clean_text_has_no_notes(self):
        data = self.data(
            "xprez_module_update",
            {"module": self.text.pk, "fields": {"text": "<p>Fine</p>"}},
        )
        self.assertNotIn("notes", data)


class GuideFollowsSettingsTest(SimpleTestCase):
    """The guide states the project's configuration, not xprez's defaults."""

    @override_settings(
        XPREZ_CK_EDITOR_FULL_CONFIG={
            "toolbar": ("bold", "heading"),
            "blockToolbar": (),
            "heading": {"options": ({"model": "h3", "view": "h3"},)},
        }
    )
    def test_text_rules_from_editor_config(self):
        from xprez.contrib.xprez_mcp.guide import render_topic

        text = render_topic("text")
        self.assertIn("Headings start at `h3`", text)
        self.assertIn("- `strong`", text)
        self.assertNotIn("- `ul`", text)

    @override_settings(
        XPREZ_BREAKPOINTS={
            0: {"name": "All", "max_width": None},
            1: {"name": "Phones", "max_width": 600},
        }
    )
    def test_breakpoints_from_settings(self):
        from xprez.contrib.xprez_mcp.guide import render_topic

        layout = render_topic("layout")
        self.assertIn("- `1`: Phones", layout)
        self.assertNotIn("Tablets", layout)


@skipUnless(MCP_INSTALLED, "needs django-xprez-mcp")
class ItemWriteTest(McpTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.numbers = xprez_models.NumbersModule.build()
        cls.numbers.section = cls.section
        cls.numbers.saved = True
        cls.numbers.position = 2
        cls.numbers.save(no_initial_item=True)
        cls.first = xprez_models.NumbersItem.objects.create(
            module=cls.numbers, number=10, caption="Years", saved=True, position=0
        )
        cls.second = xprez_models.NumbersItem.objects.create(
            module=cls.numbers, number=200, caption="Clients", saved=True, position=1
        )

    def items(self):
        return list(
            self.numbers.items.order_by("position").values_list(
                "pk", "position", "caption"
            )
        )

    def test_add(self):
        data = self.data(
            "xprez_item_add",
            {
                "module": self.numbers.pk,
                "position": 0,
                "fields": {"number": 5, "caption": "Offices"},
            },
        )
        new = data["items"][0]
        self.assertEqual((new["number"], new["caption"]), (5, "Offices"))
        self.assertEqual(
            self.items(),
            [
                (new["id"], 0, "Offices"),
                (self.first.pk, 1, "Years"),
                (self.second.pk, 2, "Clients"),
            ],
        )
        self.assertTrue(xprez_models.NumbersItem.objects.get(pk=new["id"]).saved)

    def test_update_keeps_other_items(self):
        self.data(
            "xprez_item_update",
            {
                "module": self.numbers.pk,
                "item": self.first.pk,
                "fields": {"caption": "Age"},
            },
        )
        self.assertEqual(
            self.items(),
            [(self.first.pk, 0, "Age"), (self.second.pk, 1, "Clients")],
        )
        self.first.refresh_from_db()
        self.assertEqual(self.first.number, 10)  # not sent, kept

    def test_update_invalid(self):
        message = self.error(
            "xprez_item_update",
            {
                "module": self.numbers.pk,
                "item": self.first.pk,
                "fields": {"number": "x"},
            },
        )
        self.assertIn(f"items.{self.first.pk}.number", message)

    def test_move_and_delete(self):
        self.data(
            "xprez_item_move",
            {"module": self.numbers.pk, "item": self.second.pk, "position": 0},
        )
        self.assertEqual(
            [pk for pk, _position, _caption in self.items()],
            [self.second.pk, self.first.pk],
        )
        self.data(
            "xprez_item_delete", {"module": self.numbers.pk, "item": self.second.pk}
        )
        self.assertEqual(self.items(), [(self.first.pk, 0, "Years")])

    def test_errors(self):
        self.assertIn(
            "has no items",
            self.error("xprez_item_add", {"module": self.text.pk}),
        )
        self.assertIn(
            "has no item 999999",
            self.error(
                "xprez_item_update",
                {"module": self.numbers.pk, "item": 999999, "fields": {}},
            ),
        )

    def test_rich_text_item_cleaned(self):
        accordion = xprez_models.AccordionModule.build()
        accordion.section = self.section
        accordion.saved = True
        accordion.save()  # starts with one empty item, as in the admin
        initial = accordion.items.get()
        data = self.data(
            "xprez_item_update",
            {
                "module": accordion.pk,
                "item": initial.pk,
                "fields": {"title": "Why?", "text": "<p>Because<script>x</script></p>"},
            },
        )
        self.assertEqual(data["items"][0]["text"], "<p>Because</p>")
        self.assertIn("removed tags: script", data["notes"][0])

    def test_gallery_item_needs_a_file(self):
        message = self.error("xprez_item_add", {"module": self.gallery.pk})
        self.assertIn(".file:", message)


@skipUnless(MCP_INSTALLED, "needs django-xprez-mcp")
class DraftsTest(McpTestCase):
    """Unsaved additions from an admin page are not seen or counted."""

    def visible_sections(self):
        content = self.data("xprez_container_get", {"container": self.page.pk})
        return [section["id"] for section in content["sections"]]

    def draft_module(self):
        draft = xprez_models.TextModule.build()
        draft.section = self.section
        draft.position = 0
        draft.save()
        return draft

    def test_section_positions_skip_drafts(self):
        xprez_models.Section.objects.filter(pk=self.section.pk).update(position=1)
        draft = xprez_models.Section.objects.create(container=self.page, position=0)
        last = xprez_models.Section.objects.create(
            container=self.page, saved=True, position=2
        )
        self.data("xprez_section_move", {"section": self.section.pk, "position": 1})
        self.assertEqual(self.visible_sections(), [last.pk, self.section.pk])
        draft.refresh_from_db()
        self.assertEqual(draft.position, 2)

    def test_module_positions_skip_drafts(self):
        self.draft_module()
        self.data("xprez_module_move", {"module": self.text.pk, "position": 1})
        modules = self.data("xprez_container_get", {"container": self.page.pk})[
            "sections"
        ][0]["modules"]
        self.assertEqual(
            [module["id"] for module in modules], [self.gallery.pk, self.text.pk]
        )

    def test_drafts_not_found(self):
        draft = self.draft_module()
        message = self.error(
            "xprez_module_update", {"module": draft.pk, "fields": {"text": "<p>x</p>"}}
        )
        self.assertIn("does not exist", message)
        draft.refresh_from_db()
        self.assertFalse(draft.saved)
        section = xprez_models.Section.objects.create(container=self.page)
        self.error("xprez_section_update", {"section": section.pk, "fields": {}})
        self.error(
            "xprez_module_add", {"type": "text", "section": section.pk, "fields": {}}
        )


@skipUnless(MCP_INSTALLED, "needs django-xprez-mcp")
class ExcludedModulesTest(McpTestCase):
    """XPREZ_MODULES_MCP_EXCLUDE keeps modules from agents."""

    def types(self):
        result = self.data("xprez_module_types", {"container": self.page.pk})
        return {entry["type"] for entry in result["types"]}

    def code_module(self):
        module = xprez_models.CodeInputModule.build()
        module.section = self.section
        module.saved = True
        module.position = 2
        module.code = "<b>old</b>"
        module.save()
        return module

    def test_offered_by_default(self):
        self.assertIn("codeinput", self.types())
        module = self.code_module()
        self.data(
            "xprez_module_update", {"module": module.pk, "fields": {"code": "<i>x</i>"}}
        )
        module.refresh_from_db()
        self.assertEqual(module.code, "<i>x</i>")

    @override_settings(XPREZ_MODULES_MCP_EXCLUDE=("xprez.CodeInputModule",))
    def test_excluded(self):
        self.assertNotIn("codeinput", self.types())
        self.assertIn("text", self.types())
        self.assertNotIn("codeinput", self.data("xprez_guide", {"topic": "modules"}))
        message = self.error(
            "xprez_module_add", {"type": "codeinput", "section": self.section.pk}
        )
        self.assertIn("type must be one of", message)
        module = self.code_module()
        self.assertEqual(
            self.data("xprez_module_get", {"module": module.pk})["fields"]["code"],
            "<b>old</b>",
        )
        message = self.error(
            "xprez_module_update",
            {"module": module.pk, "fields": {"code": "<script>x</script>"}},
        )
        self.assertIn("cannot be changed over MCP", message)
        self.data("xprez_module_move", {"module": module.pk, "position": 0})
        self.data("xprez_module_delete", {"module": module.pk})


@skipUnless(MCP_INSTALLED, "needs django-xprez-mcp")
class TemplatesTest(McpTestCase):
    def test_templates_are_containers(self):
        template = xprez_models.TemplateContainer.objects.create()
        result = self.data("xprez_containers_list", {"type": "xprez.templatecontainer"})
        self.assertEqual([row["id"] for row in result["results"]], [template.pk])
        self.data("xprez_section_add", {"container": template.pk})


def png_base64():
    from PIL import Image

    buffer = io.BytesIO()
    Image.new("RGB", (4, 3), "red").save(buffer, "PNG")
    return base64.b64encode(buffer.getvalue()).decode()


@skipUnless(MCP_INSTALLED, "needs django-xprez-mcp")
class FilesTest(McpTestCase):
    """File fields take django-xprez-mcp's file arguments."""

    def setUp(self):
        self.media_root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.media_root)
        override = override_settings(MEDIA_ROOT=self.media_root)
        override.enable()
        self.addCleanup(override.disable)

    def stored(self):
        return sorted(
            str(path.relative_to(self.media_root))
            for path in Path(self.media_root).rglob("*")
            if path.is_file()
        )

    def test_gallery_item_with_image(self):
        data = self.data(
            "xprez_item_add",
            {
                "module": self.gallery.pk,
                "fields": {
                    "file": {"data": png_base64(), "name": "team.png"},
                    "alt_text": "Team",
                },
            },
        )
        item = data["items"][-1]
        self.assertEqual(item["alt_text"], "Team")
        self.assertEqual(item["file"]["path"], "gallery/team.png")
        self.assertEqual(self.stored(), ["gallery/team.png"])

    def test_files_item(self):
        files = xprez_models.FilesModule.build()
        files.section = self.section
        files.saved = True
        files.save()
        content = base64.b64encode(b"%PDF-1.4 price list").decode()
        data = self.data(
            "xprez_item_add",
            {
                "module": files.pk,
                "fields": {"file": {"data": content, "name": "prices.pdf"}},
            },
        )
        self.assertEqual(data["items"][0]["file"]["path"], "files/prices.pdf")

    def test_text_media_set_and_cleared(self):
        data = self.data(
            "xprez_module_update",
            {
                "module": self.text.pk,
                "fields": {"media": {"data": png_base64(), "name": "hero.png"}},
            },
        )
        self.assertEqual(data["fields"]["media"]["path"], "images/hero.png")
        self.assertEqual(data["fields"]["text"], "<h2>Hello</h2><p>World</p>")
        data = self.data(
            "xprez_module_update", {"module": self.text.pk, "fields": {"media": None}}
        )
        self.assertIsNone(data["fields"]["media"])

    def test_invalid_image_stores_nothing(self):
        message = self.error(
            "xprez_item_add",
            {
                "module": self.gallery.pk,
                "fields": {
                    "file": {
                        "data": base64.b64encode(b"not an image").decode(),
                        "name": "fake.png",
                    }
                },
            },
        )
        self.assertIn(".file:", message)
        self.assertEqual(self.stored(), [])
        self.assertEqual(self.gallery.items.count(), 1)

    def test_required_file_cannot_be_cleared(self):
        item = self.gallery.items.get()
        message = self.error(
            "xprez_item_update",
            {"module": self.gallery.pk, "item": item.pk, "fields": {"file": None}},
        )
        self.assertIn("cannot be cleared", message)

    def test_without_sources_files_are_read_only(self):
        from xprez.contrib.xprez_mcp.provider import XprezProvider

        self.addCleanup(
            setattr, XprezProvider, "file_sources", XprezProvider.file_sources
        )
        XprezProvider.file_sources = ()
        schema = self.data(
            "xprez_module_types", {"container": self.page.pk, "type": "text"}
        )
        self.assertNotIn("media", schema["fields"])
        message = self.error(
            "xprez_module_update",
            {
                "module": self.text.pk,
                "fields": {"media": {"data": "eA==", "name": "a"}},
            },
        )
        self.assertIn("fields.media is read-only", message)
