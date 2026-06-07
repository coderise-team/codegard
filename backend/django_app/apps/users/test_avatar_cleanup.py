"""
Tests for avatar cleanup: when an avatar is replaced, cleared, or the user is
deleted, the source file is removed from storage and sorl's thumbnail cleanup
is triggered (the source's thumbnail references are dropped from the KV store).

Note on thumbnails: we assert thumbnail cleanup via sorl's KV store rather than
raw thumbnail-file existence. In tests we swap STORAGES to a temp FileSystem
backend, but sorl serializes the storage of each cached thumbnail at creation
time, so a deleted thumbnail's file may be looked up in a different location
than the test's default_storage. In production storage is constant (R2), so the
files themselves are removed. The KV-store assertion reliably proves that
`thumbnail_delete` ran and purged the thumbnail references.
"""

import io

import pytest
from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from sorl.thumbnail import default as sorl_default
from sorl.thumbnail import get_thumbnail
from sorl.thumbnail.images import ImageFile


@pytest.fixture
def fs_storage(settings, tmp_path):
    settings.STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
            "OPTIONS": {"location": str(tmp_path / "media")},
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    }
    settings.THUMBNAIL_PREFIX = "thumbnails/"

    # sorl caches its storage/kvstore in module-level LazyObjects that don't
    # react to a per-test STORAGES swap. Reset them so sorl uses the test storage.
    from django.utils.functional import empty

    for attr in ("storage", "kvstore", "engine", "backend"):
        obj = getattr(sorl_default, attr)
        if hasattr(obj, "_wrapped"):
            obj._wrapped = empty
    return settings


def _image_file(name="avatar.png", color=(255, 0, 0)):
    buf = io.BytesIO()
    Image.new("RGB", (400, 400), color=color).save(buf, format="PNG")
    buf.seek(0)
    return SimpleUploadedFile(name, buf.read(), content_type="image/png")


def _make_user_with_avatar(username, color=(255, 0, 0)):
    User = get_user_model()
    user = User.objects.create_user(
        username=username, email=f"{username}@test.com", password="pass"
    )
    user.avatar = _image_file(color=color)
    user.save()
    # Generate thumbnails so the source gets thumbnail references in the KV store.
    get_thumbnail(user.avatar, "128x128", crop="center", quality=85)
    get_thumbnail(user.avatar, "256x256", crop="center", quality=85)
    return user


def _source_has_thumbnail_refs(name: str) -> bool:
    """True if sorl still tracks thumbnails for the given source name."""
    return sorl_default.kvstore.get(ImageFile(name)) is not None


@pytest.mark.django_db
def test_old_avatar_and_thumbnails_deleted_on_replace(fs_storage):
    user = _make_user_with_avatar("u_replace")
    old_avatar = user.avatar.name

    assert default_storage.exists(old_avatar)
    assert _source_has_thumbnail_refs(old_avatar)

    user.avatar = _image_file(color=(0, 255, 0))
    user.save()

    assert not default_storage.exists(old_avatar)
    assert not _source_has_thumbnail_refs(old_avatar)
    assert default_storage.exists(user.avatar.name)


@pytest.mark.django_db
def test_avatar_and_thumbnails_deleted_on_clear(fs_storage):
    user = _make_user_with_avatar("u_clear")
    old_avatar = user.avatar.name

    assert default_storage.exists(old_avatar)
    assert _source_has_thumbnail_refs(old_avatar)

    user.avatar = None
    user.save()

    assert not default_storage.exists(old_avatar)
    assert not _source_has_thumbnail_refs(old_avatar)


@pytest.mark.django_db
def test_avatar_and_thumbnails_deleted_on_user_delete(fs_storage):
    user = _make_user_with_avatar("u_delete")
    old_avatar = user.avatar.name

    assert default_storage.exists(old_avatar)
    assert _source_has_thumbnail_refs(old_avatar)

    user.delete()

    assert not default_storage.exists(old_avatar)
    assert not _source_has_thumbnail_refs(old_avatar)
