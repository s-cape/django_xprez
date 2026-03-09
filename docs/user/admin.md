Admin
=====

XprezAdmin
----------

Register your Container models with `XprezAdmin` to get the full editing UI: sections, modules, and layout controls.

```python
from django.contrib import admin
from xprez.admin import XprezAdmin
from .models import Page

@admin.register(Page)
class PageAdmin(XprezAdmin):
    pass
```

Adding and reordering
---------------------

Add modules via the add menu. Drag to reorder modules within a section and sections within a container. Changes are saved when you submit the page form.

Clipboard
---------

Clip modules or sections to the clipboard, then paste into another page or paste as symlink to reuse the same content across containers.

Duplicate
---------

Duplicate a module or section to create a copy in the same or another container.

Symlinks
--------

Section symlinks and module symlinks let you reference the same content in multiple places without copying. Edits to the original are reflected everywhere it is linked.
