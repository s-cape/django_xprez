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

2. Make sure request context processor is enabled:


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


2. Include the xprez URLconf in your project urls.py like this:

```
    url(r'^xprez/', include('xprez.urls')),
```

3. Run `python manage.py migrate` to create xprez models.

4. ... todo


Development
-----------

To re-build ckeditor:

    cd xprez/ck_editor/assets/ckeditor5
    npm install
    npm run build


TODO
-------

- fix template content to save only relative path to database
- check template content raising UnicodeDecodeError

