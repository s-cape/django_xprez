Settings
========

Module selection
----------------

- `XPREZ_MODULES_ALLOWED` — restrict which modules can be used (default: `"__all__"`)
- `XPREZ_MODULES_ALLOWED_EXCLUDE` — exclude specific modules from allowed list
- `XPREZ_MODULES_ADD_MENU` — explicit list for the add menu (default: `None` = same as allowed)
- `XPREZ_MODULES_ADD_MENU_EXCLUDE` — exclude from add menu (default: `("xprez.ModuleSymlink",)`)

```python
# Only text, gallery, and your custom module
XPREZ_MODULES_ALLOWED = ["xprez.TextModule", "xprez.GalleryModule", "myapp.TeamModule"]

# Exclude anchor from add menu but allow pasting
XPREZ_MODULES_ADD_MENU_EXCLUDE = ("xprez.ModuleSymlink", "xprez.AnchorModule")
```

Autoregister
------------

- `XPREZ_MODULES_AUTOREGISTER` — auto-register modules on startup (default: `True`)
- `XPREZ_MODULES_AUTOREGISTER_BUILTINS` — which built-in modules to register
- `XPREZ_MODULES_AUTOREGISTER_CUSTOM` — which custom modules to register (default: `"__all__"`)

Code templates
--------------

- `XPREZ_CODE_TEMPLATES_DIR` — directory for code template files (default: `None`)
- `XPREZ_CODE_TEMPLATES_PREFIX` — URL prefix for code templates (default: `"xprez/code_templates"`)

URLs and media
--------------

- `XPREZ_USE_ABSOLUTE_URI` — use absolute URLs for media (default: `False`)
- `XPREZ_BASE_URL` — base URL when `XPREZ_USE_ABSOLUTE_URI` is `True`
- `XPREZ_FRONT_MEDIA_JS` / `XPREZ_FRONT_MEDIA_CSS` — extra JS/CSS merged with module front media

```python
# Absolute URLs for emails or headless
XPREZ_USE_ABSOLUTE_URI = True
XPREZ_BASE_URL = "https://example.com"

# Add global frontend styles
XPREZ_FRONT_MEDIA_CSS = {"all": ("myapp/css/xprez-overrides.css",)}
```

Thumbnails
----------

- `THUMBNAIL_BACKEND` — use xprez backend for SEO-friendly thumbnail filenames, or lazy generation (see below)

```python
# SEO-friendly filenames only (see xprez/contrib/sorl_thumbnail/naming/backend.py)
THUMBNAIL_BACKEND = "xprez.contrib.sorl_thumbnail.NamingThumbnailBackend"

# Lazy generation only (defer thumbnail creation until the browser requests the image)
THUMBNAIL_BACKEND = "xprez.contrib.sorl_thumbnail.LazyThumbnailBackend"

# Lazy + SEO-friendly filenames
THUMBNAIL_BACKEND = "xprez.contrib.sorl_thumbnail.LazyNamingThumbnailBackend"
```

The lazy backend returns a signed URL for missing thumbnails; the thumbnail is generated on first browser request and the browser is redirected to the real file. Include `xprez.urls` as usual so the lazy route (`xprez/thumbnail/lazy/...`) is registered. URLs are authenticated with an HMAC derived from Django `SECRET_KEY`.

Video providers
---------------

- `XPREZ_VIDEO_PROVIDERS` — list of video provider class paths (YouTube, Vimeo by default)

Breakpoints
-----------

- `XPREZ_BREAKPOINTS` — responsive breakpoint definitions (base, desktop, tablet, mobile, etc.)

```python
# Simpler breakpoint set: base, tablet, mobile
XPREZ_BREAKPOINTS = {
    0: {"name": "Base (all sizes)", "max_width": None},
    1: {"name": "Tablet (< 992px)", "max_width": 991},
    2: {"name": "Mobile (< 576px)", "max_width": 575},
}
```

Keys are breakpoint IDs; `max_width` is the max viewport width in px for that breakpoint (`None` for base = all sizes).

CSS
---

- `XPREZ_CSS` — maps layout choices (max_width, gap, padding, etc.) to CSS units and values per breakpoint. User settings are deep-merged with defaults. Use `units` (choice → unit string) and `values` (choice → `{breakpoint_id: numeric_value}`).

```python
from xprez import constants

# Section max-width "medium" = 1400px at breakpoint 0
XPREZ_CSS = {
    "section": {
        "max_width": {
            "units": {constants.MAX_WIDTH_MEDIUM: "px"},
            "values": {constants.MAX_WIDTH_MEDIUM: {0: 1400}},
        },
    },
}
```

CKEditor
--------

- `XPREZ_CK_EDITOR_MODULE_WIDGET` — widget class used by the text module
- `XPREZ_CK_EDITOR_SIMPLE_CONFIG` / `XPREZ_CK_EDITOR_FULL_CONFIG` — editor toolbar/feature config
- `XPREZ_CK_EDITOR_FILE_UPLOAD_URL_NAME` / `XPREZ_CK_EDITOR_FILE_UPLOAD_DIR` — image upload endpoint
- `XPREZ_CK_EDITOR_LICENSE_KEY` — CKEditor license key (default: `"GPL"`)

The bundled editor is CKEditor 5, which is dual-licensed under GPL 2+ or a
commercial license. `XPREZ_CK_EDITOR_LICENSE_KEY` selects which: the default
`"GPL"` is the sentinel value required (since CKEditor v44) to run under the
open-source GPL license. This refers to CKEditor's own license, not xprez's.
If you hold a commercial CKEditor license, set your key to opt out of GPL terms:

```python
XPREZ_CK_EDITOR_LICENSE_KEY = "your-commercial-key"
```

See `xprez/conf/defaults.py` for the full list and default values.

