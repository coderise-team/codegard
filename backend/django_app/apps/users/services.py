import math

from .models import EloHistory


def calculate_elo(winner, loser, contest):
    old_winner_rating = winner.elo_rating
    old_loser_rating = loser.elo_rating
    K = 32

    expected_winner = 1 / (
        1 + math.pow(10, (old_loser_rating - old_winner_rating) / 400)
    )
    expected_loser = 1 / (
        1 + math.pow(10, (old_winner_rating - old_loser_rating) / 400)
    )

    new_winner_rating = round(old_winner_rating + K * (1 - expected_winner))
    new_loser_rating = round(old_loser_rating + K * (0 - expected_loser))

    delta_w = new_winner_rating - old_winner_rating
    delta_l = new_loser_rating - old_loser_rating

    winner.elo_rating = new_winner_rating
    loser.elo_rating = new_loser_rating

    winner.save(update_fields=["elo_rating"])
    loser.save(update_fields=["elo_rating"])

    EloHistory.objects.create(
        user=winner,
        contest=contest,
        opponent=loser,
        old_rating=old_winner_rating,
        new_rating=new_winner_rating,
        delta=delta_w,
    )

    EloHistory.objects.create(
        user=loser,
        contest=contest,
        opponent=winner,
        old_rating=old_loser_rating,
        new_rating=new_loser_rating,
        delta=delta_l,
    )
