[![PyPI version](https://badge.fury.io/py/django-xprez.svg)](https://badge.fury.io/py/django-xprez)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Django Xprez
============

A flexible Django CMS with built-in modules and easy custom modules.

The backend works well with Django admin but can also be used standalone.

Features
--------

- **Structure**
  - **Containers** — apply or extend in your own models (e.g. Page, Article).
  - **Sections** — rows with max-width, background (part of the structure).
  - **Modules** (content blocks)
    - Built-in: text, quote, gallery, files, video, numbers, code input, code template, anchor.
    - Custom: simply subclass `Module` in your app; they auto-register and appear in the same admin UI and frontend.
- **Responsive**
  - Layout (visibility, columns, padding, margin, colspan) per breakpoint.
  - Responsive images (srcset, breakpoint-aware sizes).
- **Styles**
  - Ready-made frontend CSS included.
  - Or import xprez SCSS into your build; link `/xprez/variables.css` for breakpoint variables.
- **Clipboard and symlinks** — Copy modules or sections; paste into another page or paste as symlink to reuse the same content.

Quick start
-----------

1. Install django-xprez:

```bash
pip install django-xprez
```


2. Add following apps to your settings.INSTALLED_APPS:

```python
INSTALLED_APPS = [
        ...
        'sorl.thumbnail',
        'xprez',
        ...
    ]
```

3. Run `python manage.py migrate` to create xprez models.


4. Make sure request context processor is enabled in settings:

```python
TEMPLATES = [
        ...
        'OPTIONS': {
            'context_processors': [
                ...
                'django.template.context_processors.request',
                ...
            ]
        },
        ...
    ]
```

5. Include the xprez urls in your project urls.py like this:

```python
path('xprez/', include('xprez.urls')),
```

6. Create models:

```python
from xprez.models import Container

class Page(Container):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)

    def __str__(self):
        return self.title
```

7. Register models in admin:

```python
from django.contrib import admin
from xprez.admin import XprezAdmin
from .models import Page

@admin.register(Page)
class PageAdmin(XprezAdmin):
    pass
```

8. Render page in template:

```django-html
{% load xprez %}
{% xprez_front_media page %}
{% include 'xprez/container.html' with container=page %}
```

9. (optional) Add a custom module:

```python
from xprez.models import Module

class MyModule(Module):
    title = models.CharField(max_length=200)
    count = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)

    front_template_name = "myapp/modules/my.html"

    class Meta:
        verbose_name = "My module"
```

See the [built-in modules](xprez/modules/) source for more examples.

10. (optional) Change sorl thumbnail backend in settings — for seo-friendly thumbnail filenames:

```python
THUMBNAIL_BACKEND = 'xprez.contrib.sorl_thumbnail.thumbnail_backend.NamingThumbnailBackend'
```


---

For user documentation, see [docs/user/README.md](docs/user/README.md).

For an example, see the [example_app](example_app/) in this repository.

For development and contributing, see [docs/development.md](docs/development.md).
