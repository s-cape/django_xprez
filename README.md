[![PyPI version](https://badge.fury.io/py/django-xprez.svg)](https://badge.fury.io/py/django-xprez)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Django Xprez
============

Xprez is CMS For Django

Quick start
-----------

1. Install django-xprez:
```
    pip install django-xprez
```


2. Add following apps to your settings.INSTALLED_APPS:

```
    INSTALLED_APPS = [
        ...
        'django.contrib.humanize',
        'sorl.thumbnail',
        'xprez',
        'xprez.ck_editor',
        ...
    ]
```

3. Run `python manage.py migrate` to create xprez models.


4. Make sure request context processor is enabled in settings:

```
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

5. Include the xprez admin URLconf in your project urls.py like this:

```
    path('xprez/', include('xprez.urls')),
```

6. Create models:
```
    from xprez.models import ContentsContainer

    class Page(ContentsContainer):
        title = models.CharField(max_length=255)
        slug = models.SlugField(max_length=255, unique=True)

        def __str__(self):
            return self.title
```

7. Register models in admin:
```
    from django.contrib import admin
    from xprez.admin import XprezAdmin
    from .models import Page

    @admin.register(Page)
    class PageAdmin(XprezAdmin):
        pass
```

8. Render page in template:
```
    {% load xprez %}
    {% xprez_front_media %}
    {% include 'xprez/includes/photoswipe.html' %}
    {% include 'xprez/container.html' with contents=page.contents.all %}
```

9. (optional) Change sorl thumbnail backend in settings - for seo-friendly thumbnail filenames:

```
    THUMBNAIL_BACKEND = 'xprez.contrib.sorl_thumbnail.thumbnail_backend.NamingThumbnailBackend'
```

10. (optional) Look at example_app for more comprehensive example.

Development
-----------
To setup automated black formatting connected to git commits:
- install [pre-commit](https://pre-commit.com/#installation)
- run `pre-commit install`

To rebuild ckeditor:

    cd xprez/ck_editor/assets/ckeditor5
    npm install
    npm run build

To rebuild css styles

    cd xprez/static/xprez
    npm install
    npm run build (or `watch` for developing)


Deploying new version
----------------

https://github.com/s-cape/django_xprez/actions/workflows/release.yml


TODO
-------

- add custom module tutorial to Readme
- fix template content to save only relative path to database
- check template content raising UnicodeDecodeError
- create manual for various situations (ck_editor branch)
  - using custom config and implement style sources into own building system (using get_module_path.py)
  - how to implement `xprezanchor` functionality
