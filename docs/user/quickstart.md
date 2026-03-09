Quick start
===========

Minimal path to a working page.

1. Create a Container subclass (e.g. Page):

```python
from django.db import models
from xprez.models import Container

class Page(Container):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)

    def __str__(self):
        return self.title
```

2. Register it in admin with XprezAdmin:

```python
from django.contrib import admin
from xprez.admin import XprezAdmin
from .models import Page

@admin.register(Page)
class PageAdmin(XprezAdmin):
    pass
```

3. Render the page in your template:

```django-html
{% load xprez %}
{% xprez_front_media page %}
{% xprez_container_render_front page %}
```

For a full example, see the [example_app](../../example_app/) in this repository.
