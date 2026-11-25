MCP
===

xprez content can be read and edited by AI agents (Claude, Cursor, ...) over
[MCP](https://modelcontextprotocol.io), through
[django-xprez-mcp](https://github.com/s-cape/django_xprez_mcp). It is
optional: without django-xprez-mcp installed nothing of it is imported and no
MCP server exists.

Agents see the same structure as the admin (containers, sections, modules,
items, configs per breakpoint) and change it through the same forms, so
validation and permissions are the admin's.


Setup
-----

Requires django-xprez-mcp 0.8.0 or later.

1. Install the extra:

```bash
pip install "django_xprez[mcp]"
```

2. Add the apps and the settings. `PERMISSION` decides who may use the server
   at all (a dotted path to a function, the function itself, `True` or
   `False`); `ALLOW_WRITES` lets xprez's write tools through (without it
   agents can only read):

```python
INSTALLED_APPS = [
    ...
    "xprez",
    "xprez_mcp",
    "xprez_mcp.contrib.oauth",  # sign-in for assistants, see below
]

XPREZ_MCP = {
    "PERMISSION": "xprez_mcp.permissions.allow_staff",
    "AUTHENTICATION": ["xprez_mcp.contrib.oauth.auth.access_token"],
    "ALLOW_WRITES": ["xprez"],
}
```

3. Mount the server in `urls.py` and run `python manage.py migrate`:

```python
from django.urls import include, path
from xprez_mcp import mcp

urlpatterns = [
    ...
    path("", include("xprez_mcp.contrib.oauth.well_known")),  # OAuth metadata
    path("mcp/", mcp.urls),
]
```

xprez's tools are registered on `mcp` automatically (django-xprez-mcp
discovers `xprez/mcp.py`). `python manage.py mcp_inspect` lists them.

4. Connect a client. With OAuth it only needs the URL; the user signs in with
   the site's login and allows the client:

```bash
claude mcp add --transport http mysite https://example.com/mcp/
```

   In claude.ai, add `https://example.com/mcp/` as a custom connector.

### Signing in

django-xprez-mcp offers two ways, each an optional app; enable one or both:

| | `xprez_mcp.contrib.oauth` | `xprez_mcp.contrib.tokens` |
|---|---|---|
| The user | pastes the server URL, signs in, clicks "Allow" | creates a key under "MCP tokens" in the admin and pastes it into the client |
| Suits | claude.ai and ChatGPT connectors, Claude Code, Cursor | scripts, CI, clients without OAuth |
| `AUTHENTICATION` | `"xprez_mcp.contrib.oauth.auth.access_token"` | `"xprez_mcp.auth.bearer_token"` (the default) |

With both, list the OAuth backend first. OAuth also needs the site's login
(`LOGIN_URL`), a daily `python manage.py mcp_oauth_cleanup`, and
`SECURE_PROXY_SSL_HEADER` behind an HTTPS proxy. See django-xprez-mcp's
[getting started](https://github.com/s-cape/django_xprez_mcp/blob/main/docs/getting-started.md)
for the details, other clients and your own token model.

It helps to tell agents where to start, in the server's instructions (sent
when a client connects):

```python
mcp.instructions = "Pages are edited with the xprez_* tools; start with xprez_guide."
```


What agents get
---------------

| Tool | |
|---|---|
| `xprez_guide` | How content is structured and how to edit it well (also as resources `xprez://guide/{topic}`) |
| `xprez_containers_list` | Find pages and other containers |
| `xprez_container_get` | A container's sections and modules, in order |
| `xprez_module_get` | One module in full: fields, configs, items |
| `xprez_module_types` | The modules a container allows, and the fields each takes |
| `xprez_section_add` / `_update` / `_move` / `_delete` | Sections |
| `xprez_link_add` | Show a section or a whole container from another page as a link (moved and deleted with the section tools) |
| `xprez_module_add` / `_update` / `_move` / `_delete` | Modules |
| `xprez_item_add` / `_update` / `_move` / `_delete` | Items of gallery, files, accordion and numbers modules |

The resource `xprez://containers/{id}` is a container rendered as on the
site, for agents to check their changes.

- **Changes are live.** Every write tool saves at once; there are no drafts.
  Each change is recorded in the container's admin history ("Changed Text
  41 (MCP)").
- **Writes go through the admin's forms**: a module's `admin_form_class`, its
  config's form, its items' form. Custom modules and forms work without extra
  code; their validation errors are returned to the agent field by field.
- **Rich text is cleaned.** HTML sent to a CKEditor field is reduced to what
  that field's editor config can produce (toolbar, heading options, link
  decorators); scripts and styles are removed. The tool result lists what was
  changed.
- **Agents can use every module the admin offers**, including code input
  (raw HTML, not cleaned). To keep some from agents, list them in
  `XPREZ_MODULES_MCP_EXCLUDE`, for example `("xprez.CodeInputModule",)`:
  they are then not offered, and existing ones are shown and can be moved
  or deleted, but neither their fields nor their items changed.
- **Templates** (`xprez.templatecontainer`) are containers like pages: agents
  can read and edit them, but not copy them into a page.
- **Files** (gallery images, downloads, a text module's media) are sent as
  django-xprez-mcp's file arguments: `{"data": <base64>, "name": "team.jpg"}`,
  `null` to clear an optional one. They go through the field's form like an
  upload in the admin; a failed write removes what it stored. See "Files"
  below to allow more sources or change the size limit.
- **Links** are checked as in the admin's clipboard: the linked modules
  must be allowed in the target container, and a container link must not
  make a container show itself.
- **Not yet:** copying content (the clipboard's paste as a copy).
- **Unsaved additions** in the admin (a section or module added to a page
  that was not saved yet) are invisible to agents and not counted in
  positions.

An admin user who saves a page in the admin while an agent edits it
overwrites the agent's changes to what was on their screen; the guide tells
agents not to edit pages that are open in the admin.


Permissions
-----------

By default the tools follow the admin. Every container model registered on
`admin.site` with an `XprezAdmin` is exposed, and a user can do through MCP
what they can do on that container's change page:

| | Comes from the container's admin |
|---|---|
| Which containers exist | `get_queryset(request)` and `xprez_get_container_qs(request)` |
| Read tools | `has_view_or_change_permission` |
| Write tools (hidden otherwise) | `has_change_permission` |
| Available modules | `xprez_add_menu_modules(container)` |

`mcp_exposed = False` on a container model or its admin keeps it out.


### Own rules

To use other rules, or containers without a `ModelAdmin`, subclass
`XprezProvider` and override its hooks. Writes still go through an
`XprezAdminMixin`, which needs no `ModelAdmin` but must set `model`:

```python
# myapp/mcp.py: discovered like admin.py
from xprez_mcp import mcp

from xprez.admin import XprezAdminMixin
from xprez.contrib.xprez_mcp.provider import XprezProvider

from .models import Page


class PageXprez(XprezAdminMixin):
    model = Page

    def xprez_allowed_modules(self, container=None):
        return ["xprez.TextModule", "xprez.GalleryModule"]


class PagesProvider(XprezProvider):
    def get_container_models(self, ctx):
        return {Page: PageXprez()}

    def get_container_queryset(self, ctx, model, xprez_admin, write=False):
        return model.objects.filter(owner=ctx.user)

    def has_container_permission(
        self, ctx, model, xprez_admin, container=None, write=False
    ):
        return ctx.user.has_perm("pages.edit_content") if write else True


mcp.unregister(XprezProvider)  # registered by xprez/mcp.py
mcp.register(PagesProvider)
```

`mcp.py` modules are imported in `INSTALLED_APPS` order, so `xprez` must
come before the app that unregisters its provider.

| Hook | Default |
|---|---|
| `get_container_models(ctx)` | the `XprezAdmin`s on `admin_site` (`XprezProvider.admin_site`, default `admin.site`) |
| `get_container_queryset(ctx, model, xprez_admin, write)` | the admin's queryset and `xprez_get_container_qs` |
| `has_container_permission(ctx, model, xprez_admin, container, write)` | the admin's view/change permission; nothing without a `ModelAdmin` |
| `search_containers(ctx, model, xprez_admin, queryset, query)` | the admin's `search_fields` |
| `log_change(ctx, model, xprez_admin, container, message)` | the admin's history; nothing without a `ModelAdmin` |

### Files

`XprezProvider` takes file arguments through django-xprez-mcp's
`FileArgumentsMixin`; its attributes set what agents may send:

| Attribute | Default |
|---|---|
| `file_sources` | `("data",)`: base64 content. Add `"path"` for files already in the field's upload folder, `"url"` for the server to fetch public URLs; `()` makes file fields read-only |
| `max_file_size` | 10 MB per file; see the request limit below |
| `file_fetch_timeout` | 10 seconds, for `"url"` |

```python
class SiteXprezProvider(XprezProvider):
    file_sources = ("data", "path")


mcp.unregister(XprezProvider)
mcp.register(SiteXprezProvider)
```

A base64 file travels in the JSON request, which Django caps with
`DATA_UPLOAD_MAX_MEMORY_SIZE` (2.5 MB by default). Base64 adds a third, so
by default files over about 1.8 MB fail with "Request too large." Raise the
setting for larger files, for example `DATA_UPLOAD_MAX_MEMORY_SIZE = 15 *
1024 * 1024` for 10 MB files. The `"path"` and `"url"` sources are not
limited by it.

`allows_file_path` and `fetch_file` can be overridden for stricter rules;
see django-xprez-mcp's docs on file arguments.

To drop xprez's tools from a server, `mcp.unregister(XprezProvider)` or
`XPREZ_MCP["EXCLUDE_APPS"] = ["xprez"]`.


The guide
---------

`xprez_guide` serves short texts for agents: `index`, `editing`, `layout`,
`modules`, `text`. They state your configuration, not xprez's defaults:
breakpoints from `XPREZ_BREAKPOINTS`, allowed HTML and heading levels from
the editor config, modules from `XPREZ_MODULES_ALLOWED`.

To change a topic, add a template `xprez/mcp/guide/<topic>.md` to your
project, for example with your own writing conventions. It is rendered with
the same context as the bundled texts (in
`xprez/contrib/xprez_mcp/guide/`): `topics`, `breakpoints`, `modules`,
`text_rules`, `headings`, `columns`.

A custom module describes itself for the `modules` topic with
`mcp_summary`:

```python
class TeamModule(MultiModule):
    mcp_summary = "Team members, each with a photo, name and role."
```
