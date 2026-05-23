"""
Scoring logic for contests.

Formula:
  base_points = 100 per solved problem
  penalty     = 10 minutes per wrong attempt on each solved problem
                + minutes from contest start to AC time

  score       = sum of base_points across all solved problems
  leaderboard = sorted by score DESC, penalty ASC, last_ac_at ASC
"""

from django.db import transaction

from .models import Contest, ContestScore

BASE_POINTS = 100
WRONG_ATTEMPT_PENALTY_MINUTES = 10


def calculate_score(user, contest: Contest) -> ContestScore:
    """
    Recalculate ContestScore for a user in a contest.
    Called after every new AC submission.

    Returns the updated ContestScore instance.
    """
    from apps.submissions.models import Submission

    submissions = Submission.objects.filter(user=user, contest=contest).order_by(
        "created_at"
    )

    total_score = 0
    total_penalty = 0
    solved_count = 0
    last_ac_at = None

    # Group by problem (remove ordering to keep DISTINCT stable)
    problem_ids = submissions.order_by().values_list("problem_id", flat=True).distinct()

    for problem_id in problem_ids:
        problem_subs = submissions.filter(problem_id=problem_id)

        # Check if this problem was solved (has AC)
        ac_submission = problem_subs.filter(verdict=Submission.Verdict.AC).first()
        if not ac_submission:
            continue  # Not solved — no points, no penalty

        # Count wrong attempts BEFORE the first AC
        wrong_attempts = problem_subs.filter(
            verdict__in=[
                Submission.Verdict.WA,
                Submission.Verdict.TLE,
                Submission.Verdict.MLE,
                Submission.Verdict.RE,
                Submission.Verdict.CE,
            ],
            created_at__lt=ac_submission.created_at,
        ).count()

        # Time penalty: minutes from contest start to AC
        time_penalty = int(
            (ac_submission.created_at - contest.start_time).total_seconds() / 60
        )

        # Penalty from wrong attempts
        attempt_penalty = wrong_attempts * WRONG_ATTEMPT_PENALTY_MINUTES

        total_score += BASE_POINTS
        total_penalty += time_penalty + attempt_penalty
        solved_count += 1

        if last_ac_at is None or ac_submission.created_at > last_ac_at:
            last_ac_at = ac_submission.created_at

    with transaction.atomic():
        contest_score, _ = ContestScore.objects.update_or_create(
            user=user,
            contest=contest,
            defaults={
                "score": total_score,
                "penalty": total_penalty,
                "solved_count": solved_count,
                "last_ac_at": last_ac_at,
            },
        )

    return contest_score


def get_leaderboard(contest: Contest):
    """
    Return leaderboard queryset for a contest.
    Sorted by: score DESC → penalty ASC → last_ac_at ASC
    """
    return (
        ContestScore.objects.filter(contest=contest)
        .select_related("user")
        .order_by("-score", "penalty", "last_ac_at")
    )
