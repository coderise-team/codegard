# ruff: noqa: F403, F405
from .base import *

DEBUG = True

SECRET_KEY = env(
    "SECRET_KEY", default="django-insecure-dev-only-do-not-use-in-production"
)

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

DATABASES = {
    "default": env.db(
        "DATABASE_URL", default="postgres://postgres:postgres@localhost:5432/codegard"
    )
}

INTERNAL_IPS = ["127.0.0.1"]

INSTALLED_APPS += ["debug_toolbar"]

MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware"] + MIDDLEWARE
