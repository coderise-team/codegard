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


def apply_contest_ratings(contest: Contest) -> int:
    """
    Award ELO for one finished contest. Returns the number of participants updated.

    Idempotent: locks the Contest row and re-checks `rating_applied`, so two
    overlapping beat runs never double-count. Everything is one transaction, so
    a mid-flight crash rolls back and the contest is retried next run.

    Rating set = everyone who made >=1 submission. Those who solved nothing get
    score=0 / last place and a freshly created ContestScore. Pure no-shows
    (joined but never submitted) are not rated.
    """
    from apps.submissions.models import Submission
    from apps.users.models import EloHistory, User
    from apps.users.services import EloParticipant, compute_elo_deltas

    with transaction.atomic():
        # 1. Lock the contest and re-check the flag (the task's filter is not enough).
        contest = Contest.objects.select_for_update().get(pk=contest.pk)
        if contest.rating_applied:
            return 0

        # 2. Build the set: everyone who submitted at least once.
        submitter_ids = set(
            Submission.objects.filter(contest=contest)
            .values_list("user_id", flat=True)
            .distinct()
        )
        scored = list(get_leaderboard(contest))  # ContestScore rows, in place order
        scored_uids = {cs.user_id for cs in scored}
        # Submitted but solved nothing → last place, no ContestScore yet.
        zero_ids = [uid for uid in submitter_ids if uid not in scored_uids]
        ordered_uids = [cs.user_id for cs in scored] + zero_ids

        # 3. Degenerate field (0 or 1 rated) — no opponents, just mark done.
        if len(ordered_uids) < 2:
            contest.rating_applied = True
            contest.save(update_fields=["rating_applied"])
            return 0

        # 4. Lock users (stable order, anti-deadlock) and snapshot ratings BEFORE.
        users = {
            u.id: u
            for u in User.objects.select_for_update()
            .filter(id__in=ordered_uids)
            .order_by("id")
        }
        snapshot = {uid: users[uid].elo_rating for uid in ordered_uids}

        # 5. Ordered-by-place participants → pure ELO (deltas off the snapshot).
        participants = [
            EloParticipant(
                user_id=cs.user_id,
                rating=snapshot[cs.user_id],
                place_key=(cs.score, cs.penalty, cs.last_ac_at),
            )
            for cs in scored
        ] + [
            EloParticipant(user_id=uid, rating=snapshot[uid], place_key=(0, 0, None))
            for uid in zero_ids
        ]
        deltas = compute_elo_deltas(participants)

        # 6. Apply (one save per row — fields chosen so the avatar signal skips).
        scored_by_uid = {cs.user_id: cs for cs in scored}
        for uid in ordered_uids:
            user = users[uid]
            new_rating = snapshot[uid] + deltas[uid]
            user.elo_rating = new_rating
            user.max_rating = max(user.max_rating, new_rating)
            user.save(update_fields=["elo_rating", "max_rating"])

            cs = scored_by_uid.get(uid)
            if cs is not None:
                cs.rating_delta = deltas[uid]
                cs.rating_after = new_rating
                cs.save(update_fields=["rating_delta", "rating_after"])
            else:
                ContestScore.objects.create(
                    user=user,
                    contest=contest,
                    score=0,
                    penalty=0,
                    solved_count=0,
                    last_ac_at=None,
                    rating_delta=deltas[uid],
                    rating_after=new_rating,
                )
            EloHistory.objects.create(user=user, rating=new_rating)

        # 7. Mark done in the same transaction.
        contest.rating_applied = True
        contest.save(update_fields=["rating_applied"])

    return len(ordered_uids)
