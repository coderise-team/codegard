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

try:
    import debug_toolbar  # noqa: F401
except ModuleNotFoundError:
    # `django-debug-toolbar` is a dev-only dependency. If it's not installed
    # (e.g. slim/CI images), keep the dev settings usable instead of crashing.
    pass
else:
    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware"] + MIDDLEWARE
