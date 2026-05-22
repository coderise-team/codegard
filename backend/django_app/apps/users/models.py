import uuid
from pathlib import Path

from django.contrib.auth.models import AbstractUser
from django.db import models


def user_avatar_upload_to(_instance, filename: str) -> str:
    ext = Path(filename).suffix.lower()
    ext = ext if ext in {".jpg", ".jpeg", ".png", ".webp"} else ".jpg"
    return f"avatars/{uuid.uuid4().hex}{ext}"


class User(AbstractUser):
    email = models.EmailField(unique=True)
    avatar = models.ImageField(upload_to=user_avatar_upload_to, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    elo_rating = models.IntegerField(blank=True, null=True)
