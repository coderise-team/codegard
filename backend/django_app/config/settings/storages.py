"""
Cloudflare R2 storage configuration via django-storages (S3-compatible).

This module is imported from settings/base.py to optionally override STORAGES.
"""

import os


def _env_bool(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


R2_ACCOUNT_ID = os.environ.get("R2_ACCOUNT_ID", "")
R2_ACCESS_KEY_ID = os.environ.get("R2_ACCESS_KEY_ID", "")
R2_SECRET_ACCESS_KEY = os.environ.get("R2_SECRET_ACCESS_KEY", "")
R2_BUCKET_NAME = os.environ.get("R2_BUCKET_NAME", "")
R2_CUSTOM_DOMAIN = os.environ.get("R2_CUSTOM_DOMAIN", "")

R2_QUERYSTRING_AUTH = _env_bool("R2_QUERYSTRING_AUTH", default=not bool(R2_CUSTOM_DOMAIN))
R2_QUERYSTRING_EXPIRE = int(os.environ.get("R2_QUERYSTRING_EXPIRE", "604800"))

R2_ENABLED = all([R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET_NAME])

if R2_ENABLED:
    storage_options = {
        "access_key": R2_ACCESS_KEY_ID,
        "secret_key": R2_SECRET_ACCESS_KEY,
        "bucket_name": R2_BUCKET_NAME,
        "endpoint_url": f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
        "region_name": "auto",
        "signature_version": "s3v4",
        "default_acl": None,
        "file_overwrite": False,
        "location": "media",
        "querystring_auth": R2_QUERYSTRING_AUTH,
        **({"custom_domain": R2_CUSTOM_DOMAIN} if R2_CUSTOM_DOMAIN else {}),
        **({"querystring_expire": R2_QUERYSTRING_EXPIRE} if R2_QUERYSTRING_AUTH else {}),
    }

    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3.S3Storage",
            "OPTIONS": storage_options,
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
else:
    STORAGES = {
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }


THUMBNAIL_QUALITY = 85
THUMBNAIL_FORMAT = "WEBP"
THUMBNAIL_PRESERVE_FORMAT = False
THUMBNAIL_COLORSPACE = "RGB"

THUMBNAIL_PREFIX = "thumbnails/"
THUMBNAIL_CACHE_TIMEOUT = 60 * 60 * 24 * 30

# IMPORTANT:
# Do not set THUMBNAIL_STORAGE to a raw backend path like "storages.backends.s3.S3Storage".
# That makes sorl-thumbnail instantiate a brand-new storage without our R2 OPTIONS, which
# results in Unauthorized/AccessDenied when uploading thumbnails.
#
# By leaving THUMBNAIL_STORAGE unset, sorl-thumbnail will use Django's default storage
# (which is already configured above via STORAGES["default"]).

THUMBNAIL_KVSTORE = "sorl.thumbnail.kvstores.cached_db_kvstore.KVStore"

THUMBNAIL_DEBUG = False
THUMBNAIL_UPSCALE = False
