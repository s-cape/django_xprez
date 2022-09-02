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
        'xprez.ck_editor',
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


Deploying to pip
----------------

# requirements

    python -m pip install --user --upgrade setuptools wheel twine


# cleanup old builds (if exists)

    rm -rf ./dist ./build

# create dist package

    python setup.py sdist bdist_wheel

# to check package add this to requirements.txt

    file:/<path_to_package>/dist/django_xprez-<version>.tar.gz

# upload to testpypi (username: jakub.dolejsek)

    python -m twine upload --repository testpypi dist/*

# to check package from testpypi add (temporary) this to top of requirements.txt:

    --extra-index-url https://test.pypi.org/simple/

# upload to pypi (username: jakub.dolejsek)

    python -m twine upload dist/*


TODO
-------

- fix template content to save only relative path to database
- check template content raising UnicodeDecodeError
- create manual for various situations (ck_editor branch)
  - using custom config and implement style sources into own building system (using get_module_path.py)
  - how to implement `xprezanchor` functionality
