============
Django Xprez
============

Xprez is CMS For Django

Quick start
-----------

1. Add following apps to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'django.contrib.humanize',
        'sorl.thumbnail',
        'xprez',
        'xprez.medium_editor',
    ]

2. Include the xprez URLconf in your project urls.py like this::

    url(r'^xprez/', include('xprez.urls')),

3. Run `python manage.py migrate` to create xprez models.

4. ... todo

