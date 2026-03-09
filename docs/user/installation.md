Installation
============

1. Install django-xprez:

```bash
pip install django-xprez
```

2. Add the following apps to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    "sorl.thumbnail",
    "xprez",
    ...
]
```

3. Run `python manage.py migrate` to create xprez models.

4. Ensure the request context processor is enabled:

```python
TEMPLATES = [
    ...
    "OPTIONS": {
        "context_processors": [
            ...
            "django.template.context_processors.request",
            ...
        ]
    },
    ...
]
```

5. Include the xprez URLs in your project `urls.py`:

```python
path("xprez/", include("xprez.urls")),
```
