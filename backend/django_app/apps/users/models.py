import uuid
from pathlib import Path

from django.conf import settings
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
    elo_rating = models.IntegerField(default=1200, blank=False, null=False)


class EloHistory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="elo_history",
        verbose_name="Пользователь",
    )
    contest = models.ForeignKey(
        "contests.Contest",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="elo_changes",
        verbose_name="Конкурс",
    )
    opponent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="elo_opponent_history",
        verbose_name="Оппонент",
    )
    old_rating = models.IntegerField(verbose_name="Рейтинг до")
    new_rating = models.IntegerField(verbose_name="Рейтинг после")
    delta = models.IntegerField(verbose_name="Изменение рейтинга")

    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Дата изменения")

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "История ELO"
        verbose_name_plural = "История ELO"
        indexes = [
            # Speeds up the elo-history query (filter by user, order by timestamp).
            models.Index(fields=["user", "timestamp"]),
        ]

    def __str__(self):
        return (
            f"{self.user.username}: {self.old_rating} -> "
            f"{self.new_rating} ({self.delta:+d})"
        )
