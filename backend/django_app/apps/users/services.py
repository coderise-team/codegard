import math
from django.db import transaction
from django.core.exceptions import ValidationError
from django.conf import settings
from .models import EloHistory

K_FACTOR = getattr(settings, 'ELO_K_FACTOR', 32)

def calculate_elo(winner, loser, contest):
    if winner == loser:
        raise ValidationError("Победитель и проигравший не могут быть одним и тем же лицом.")

    participants = contest.participants.all()
    if winner not in participants or loser not in participants:
        raise ValidationError("Один или оба игрока не являются участниками этого контеста.")

    with transaction.atomic():
        from apps.users.models import User

        winner_db = User.objects.select_for_update().get(id=winner.id)
        loser_db = User.objects.select_for_update().get(id=loser.id)

        old_winner_rating = winner_db.elo_rating
        old_loser_rating = loser_db.elo_rating

        winner_delta = 16
        loser_delta = -16

        winner_db.elo_rating = old_winner_rating + winner_delta
        winner_db.save(update_fields=["elo_rating"])

        loser_db.elo_rating = old_loser_rating + loser_delta
        loser_db.save(update_fields=["elo_rating"])

        EloHistory.objects.create(
            user=winner_db,
            contest=contest,
            old_rating=old_winner_rating,
            new_rating=winner_db.elo_rating,
            delta=winner_delta
        )
        EloHistory.objects.create(
            user=loser_db,
            contest=contest,
            old_rating=old_loser_rating,
            new_rating=loser_db.elo_rating,
            delta=loser_delta
        )
