[![PyPI version](https://badge.fury.io/py/django-xprez.svg)](https://badge.fury.io/py/django-xprez)

Django Xprez
============

Xprez is CMS For Django

Quick start
-----------

1. Install django-xprez:
```
    pip install django-xprez
```


2. Add following apps to your INSTALLED_APPS setting like this:

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

        def __unicode__(self):
            return self.__str__()
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
    {% xprez_front_media %}
    {% include 'xprez/container.html' with contents=page.contents.all %}
```

9. (optional) Change sorl thumbnail backend in settings - for seo-friendly thumbnail filenames:

```
    THUMBNAIL_BACKEND = 'xprez.contrib.sorl_thumbnail.thumbnail_backend.NamingThumbnailBackend'
```


Development
-----------

To rebuild ckeditor:

    cd xprez/ck_editor/assets/ckeditor5
    npm install
    npm run build

To rebuild css styles

    cd xprez/static/xprez
    npm install
    npm run build (or `watch` for developing)


Deploying to pip
----------------

#### requirements

    python -m pip install --user --upgrade setuptools wheel twine


#### cleanup old builds (if exists)

    rm -rf ./dist ./build

#### create dist package

    python setup.py sdist bdist_wheel

#### to check package add this to requirements.txt

    file:/<path_to_package>/dist/django_xprez-<version>.tar.gz

#### upload to testpypi (username: jakub.dolejsek)

    python -m twine upload --repository testpypi dist/*

#### to check package from testpypi add (temporary) this to top of requirements.txt:

    --extra-index-url https://test.pypi.org/simple/

#### upload to pypi (username: jakub.dolejsek)

    python -m twine upload dist/*


TODO
-------

- fix template content to save only relative path to database
- check template content raising UnicodeDecodeError
- create manual for various situations (ck_editor branch)
  - using custom config and implement style sources into own building system (using get_module_path.py)
  - how to implement `xprezanchor` functionality
