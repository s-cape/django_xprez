from .settings import *

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "xprez_example_app",
        "OPTIONS": {
            "user": "postgres",
            "password": "postgres",
            "host": "localhost",
        },
    }
}
