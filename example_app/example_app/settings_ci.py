import os

from .settings import *

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ.get("XPREZ_TEST_DB_NAME", "xprez_example_app"),
    }
}
if os.environ.get("XPREZ_TEST_DB_USER"):
    DATABASES["default"]["USER"] = os.environ.get("XPREZ_TEST_DB_USER")
    CACHES = {"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}}
if os.environ.get("XPREZ_TEST_DB_PASSWORD"):
    DATABASES["default"]["PASSWORD"] = os.environ.get("XPREZ_TEST_DB_PASSWORD")
if os.environ.get("XPREZ_TEST_DB_HOST"):
    DATABASES["default"]["HOST"] = os.environ.get("XPREZ_TEST_DB_HOST")
