"""Tests for the `channel_layer is None` early-return branches in signals.py."""

from datetime import timedelta
from unittest.mock import patch

import pytest
from apps.contests.models import Contest
from apps.problems.models import Problem
from apps.submissions.models import Submission
from apps.submissions.signals import _broadcast_leaderboard, _broadcast_problem_solved
from django.utils import timezone


@pytest.fixture
def user(db, django_user_model):
    return django_user_model.objects.create_user(username="tester", password="pass")


@pytest.fixture
def problem(db):
    return Problem.objects.create(
        title="Problem A",
        description="",
        difficulty=Problem.Difficulty.EASY,
        time_limit=1000,
        memory_limit=256,
    )


@pytest.fixture
def active_contest(db):
    now = timezone.now()
    return Contest.objects.create(
        title="Test Contest",
        start_time=now - timedelta(hours=1),
        end_time=now + timedelta(hours=2),
        status=Contest.Status.ACTIVE,
    )


@pytest.mark.django_db
def test_broadcast_leaderboard_no_channel_layer(active_contest):
    """_broadcast_leaderboard returns silently when no channel layer is configured."""
    with patch("channels.layers.get_channel_layer", return_value=None):
        # Should not raise
        _broadcast_leaderboard(active_contest)


@pytest.mark.django_db
def test_broadcast_problem_solved_no_channel_layer(user, problem, active_contest):
    """_broadcast_problem_solved returns silently when channel layer is None."""
    submission = Submission.objects.create(
        user=user,
        problem=problem,
        contest=active_contest,
        code="x=1",
        language=Submission.Language.PYTHON,
        verdict=Submission.Verdict.WA,
    )
    with patch("channels.layers.get_channel_layer", return_value=None):
        # Should not raise
        _broadcast_problem_solved(submission)
