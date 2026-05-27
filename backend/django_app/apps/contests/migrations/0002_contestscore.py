import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("contests", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ContestScore",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("score", models.IntegerField(default=0)),
                (
                    "penalty",
                    models.IntegerField(
                        default=0,
                        help_text="Total penalty in minutes.",
                    ),
                ),
                ("solved_count", models.IntegerField(default=0)),
                (
                    "last_ac_at",
                    models.DateTimeField(
                        blank=True,
                        help_text="Time of last AC submission — used for tiebreaking.",
                        null=True,
                    ),
                ),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "contest",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="scores",
                        to="contests.contest",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="contest_scores",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-score", "penalty", "last_ac_at"],
                "unique_together": {("user", "contest")},
            },
        ),
    ]
