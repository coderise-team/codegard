"""Daily-challenge streak computation.

Lives here (problems domain) because it reads DailyProblem; the user view just
calls compute_streak(). Strict LeetCode-style: a day counts only if the user
closed that day's problem with an AC made on that same day (UTC).
"""

from datetime import timedelta

from apps.submissions.models import Submission
from django.db.models.functions import TruncDate
from django.utils import timezone

from .models import DailyProblem

# Visual size of the history grid on the dashboard. Streak totals span the whole
# history; this only bounds the returned grid.
HISTORY_DAYS = 14


def compute_streak(user) -> dict:
    """Return {current_streak, longest_streak, history} for `user`.

    Exactly two DB queries; everything else is an in-memory walk (no per-day
    queries).
    """
    today = timezone.now().date()

    # 1. All assigned days up to today: {date: problem_id}.
    dailies = dict(
        DailyProblem.objects.filter(date__lte=today).values_list("date", "problem_id")
    )

    # 2. Which (day, problem) the user closed with an AC on that same day —
    #    narrowed to daily problems (a small set), so the (user, created_at)
    #    index applies, no N+1.
    solved_days = set()
    if dailies:
        solved_pairs = set(
            Submission.objects.filter(
                user=user,
                verdict=Submission.Verdict.AC,
                problem_id__in=set(dailies.values()),
            )
            .annotate(day=TruncDate("created_at"))
            .values_list("day", "problem_id")
        )
        solved_days = {d for d, pid in dailies.items() if (d, pid) in solved_pairs}

    return {
        "current_streak": _current_streak(today, solved_days),
        "longest_streak": _longest_streak(solved_days),
        "history": _history(today, solved_days),
    }


def _current_streak(today, solved_days) -> int:
    """Consecutive credited days counting back from today.

    Today not solved yet does NOT break the streak — start from yesterday.
    """
    day = today if today in solved_days else today - timedelta(days=1)
    streak = 0
    while day in solved_days:
        streak += 1
        day -= timedelta(days=1)
    return streak


def _longest_streak(solved_days) -> int:
    """Longest run of consecutive calendar days over all history."""
    if not solved_days:
        return 0
    longest = 1
    run = 1
    ordered = sorted(solved_days)
    for prev, cur in zip(ordered, ordered[1:]):
        run = run + 1 if (cur - prev).days == 1 else 1
        longest = max(longest, run)
    return longest


def _history(today, solved_days) -> list[dict]:
    """The last HISTORY_DAYS cells, oldest to newest (today−13 … today)."""
    cells = []
    for offset in range(HISTORY_DAYS - 1, -1, -1):
        day = today - timedelta(days=offset)
        if day in solved_days:
            status = "solved"
        elif day == today:
            status = "today"
        else:
            status = "missed"
        cells.append({"date": day.isoformat(), "status": status})
    return cells
