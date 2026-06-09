"""
Avatar cleanup signals.

Keeps R2 (default storage) free of orphaned avatar files and their cached
thumbnails. A single pre_save handler covers every code path that changes the
avatar field (admin replace, admin clear, API upload) because they all call
User.save(); post_delete covers user deletion.
"""

import logging

from django.core.files.storage import default_storage
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from sorl.thumbnail import delete as thumbnail_delete

from .models import User

logger = logging.getLogger(__name__)


def _delete_avatar(avatar) -> None:
    """
    Remove an avatar source file and all its cached thumbnails from storage.

    `avatar` may be an ImageFieldFile or a plain name string. Failures are
    logged but never raised, so cleanup can't block a save/delete.
    """
    if not avatar:
        return

    name = getattr(avatar, "name", avatar)

    # Remove cached thumbnails (thumbnail files + KV-store entries). delete_file
    # is False because we delete the source ourselves below — this also makes the
    # behaviour identical whether `avatar` is a field file or a plain name string.
    try:
        thumbnail_delete(avatar, delete_file=False)
    except Exception as exc:  # noqa: BLE001 - cleanup must never break the request
        logger.warning("Failed to delete thumbnails for %r: %s", name, exc)

    # Remove the source file from storage (R2 / FileSystem).
    try:
        if name and default_storage.exists(name):
            default_storage.delete(name)
    except Exception as exc:  # noqa: BLE001 - cleanup must never break the request
        logger.warning("Failed to delete avatar %r from storage: %s", name, exc)


@receiver(post_delete, sender=User)
def delete_avatar_on_user_delete(sender, instance: User, **kwargs):
    """User removed -> delete their avatar + thumbnails from R2."""
    _delete_avatar(instance.avatar)


# Attribute used to carry the orphaned old avatar from pre_save to post_save.
_STASH_ATTR = "_avatar_to_delete"


@receiver(pre_save, sender=User)
def stash_old_avatar_on_change(sender, instance: User, **kwargs):
    """
    Avatar replaced or cleared -> REMEMBER the old file (don't delete it yet).

    We only delete in post_save, after the row is safely written, so a failed
    save() can never orphan the DB row from its (already deleted) file. The old
    avatar is stashed on the instance and picked up by delete_stashed_avatar.

    Covers admin replace, admin clear, and API upload (all call save()).
    """
    if not instance.pk:
        return  # brand-new user, nothing to replace

    # Skip the extra SELECT on saves that can't touch the avatar. The avatar API
    # (views.py) already passes update_fields=["avatar"]; frequent saves like ELO
    # updates (services.py) pass other fields and don't need the old-file lookup.
    update_fields = kwargs.get("update_fields")
    if update_fields is not None and "avatar" not in update_fields:
        return

    # Fetch the previously stored row so we work with a real ImageFieldFile
    # (its .avatar) — identical to the post_delete path, so sorl can resolve and
    # delete the cached thumbnails by their source key.
    old_instance = User.objects.filter(pk=instance.pk).only("avatar").first()
    if old_instance is None or not old_instance.avatar:
        return  # had no avatar before

    new_name = instance.avatar.name if instance.avatar else ""
    if old_instance.avatar.name != new_name:
        # field changed (new file) or was cleared -> old file is now orphaned.
        # Stash it; the actual delete happens in post_save once the row is saved.
        setattr(instance, _STASH_ATTR, old_instance.avatar)


@receiver(post_save, sender=User)
def delete_stashed_avatar(sender, instance: User, **kwargs):
    """Row saved successfully -> now it's safe to delete the old avatar from R2."""
    old_avatar = getattr(instance, _STASH_ATTR, None)
    if old_avatar:
        # Clear the stash first so a re-save can't double-delete.
        setattr(instance, _STASH_ATTR, None)
        _delete_avatar(old_avatar)
