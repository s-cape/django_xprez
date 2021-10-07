Django Xprez
============

Xprez is CMS For Django

Quick start
-----------

1. Add following apps to your INSTALLED_APPS setting like this:

```
    INSTALLED_APPS = [
        ...
        'django.contrib.humanize',
        'sorl.thumbnail',
        'xprez',
        'xprez.medium_editor',
        ...
    ]
```

2. Make sure request context processor is enabled in settings:


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


3. (optional) Change sorl thumbnail backend in settings - for seo-friendly thumbnail filenames:

```
    THUMBNAIL_BACKEND = 'xprez.contrib.sorl_thumbnail.thumbnail_backend.NamingThumbnailBackend'
```


4. Include the xprez URLconf in your project urls.py like this:

```
    url(r'^xprez/', include('xprez.urls')),
```

5. Run `python manage.py migrate` to create xprez models.


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


TODO
-------

- fix template content to save only relative path to database
- check template content raising UnicodeDecodeError

