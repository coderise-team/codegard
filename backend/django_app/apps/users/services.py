from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction

from .models import EloHistory

K_FACTOR = getattr(settings, "ELO_K_FACTOR", 32)

# Rank tiers by ELO, lower bound inclusive. Highest first for a simple lookup:
# e.g. elo 1200 -> Junior, 1399 -> Junior, 1400 -> Specialist, 2400+ -> Kernel.
RANK_THRESHOLDS = [
    (2400, "Kernel"),
    (2200, "Architect"),
    (2000, "Grandmaster"),
    (1800, "Master"),
    (1600, "Expert"),
    (1400, "Specialist"),
    (1200, "Junior"),
    (0, "Trainee"),
]


def get_rank(elo: int) -> str:
    """Map an ELO rating to its rank name (computed on the fly, never stored)."""
    for threshold, name in RANK_THRESHOLDS:
        if elo >= threshold:
            return name
    return "Trainee"  # fallback for unexpected negative ratings


def calculate_elo(winner, loser, contest):
    if winner == loser:
        raise ValidationError(
            "Победитель и проигравший не могут быть одним и тем же лицом."
        )

    participants = contest.participants.all()
    if winner not in participants or loser not in participants:
        raise ValidationError(
            "Один или оба игрока не являются участниками этого контеста."
        )

    with transaction.atomic():
        from apps.users.models import User

        winner_db = User.objects.select_for_update().get(id=winner.id)
        loser_db = User.objects.select_for_update().get(id=loser.id)

        old_winner_rating = winner_db.elo_rating
        old_loser_rating = loser_db.elo_rating

        expected_winner = 1 / (1 + 10 ** ((old_loser_rating - old_winner_rating) / 400))
        expected_loser = 1 - expected_winner

        winner_delta = round(K_FACTOR * (1 - expected_winner))
        loser_delta = round(K_FACTOR * (0 - expected_loser))

        winner_db.elo_rating = old_winner_rating + winner_delta
        winner_db.save(update_fields=["elo_rating"])

        loser_db.elo_rating = old_loser_rating + loser_delta
        loser_db.save(update_fields=["elo_rating"])

        EloHistory.objects.create(
            user=winner_db,
            rating=winner_db.elo_rating,
        )
        EloHistory.objects.create(
            user=loser_db,
            rating=loser_db.elo_rating,
        )
