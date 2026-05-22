from datetime import timedelta
from unittest.mock import patch

import pytest
from apps.contests.models import Contest
from apps.problems.models import Problem
from apps.submissions.models import Submission
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db, django_user_model):
    return django_user_model.objects.create_user(
        username="user", email="user@test.com", password="pass"
    )


@pytest.fixture
def other_user(db, django_user_model):
    return django_user_model.objects.create_user(
        username="other", email="other@test.com", password="pass"
    )


@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def problem(db):
    return Problem.objects.create(
        title="Two Sum",
        description="Find two numbers.",
        difficulty="easy",
        time_limit=1000,
        memory_limit=256,
    )


@pytest.fixture
def active_contest(db, problem):
    now = timezone.now()
    contest = Contest.objects.create(
        title="Active Contest",
        start_time=now - timedelta(hours=1),
        end_time=now + timedelta(hours=1),
        status=Contest.Status.ACTIVE,
    )
    contest.problems.add(problem)
    return contest


@pytest.fixture
def finished_contest(db, problem):
    now = timezone.now()
    contest = Contest.objects.create(
        title="Finished Contest",
        start_time=now - timedelta(hours=3),
        end_time=now - timedelta(hours=1),
        status=Contest.Status.FINISHED,
    )
    contest.problems.add(problem)
    return contest


@pytest.fixture
def submission(db, user, problem):
    return Submission.objects.create(
        user=user,
        problem=problem,
        code="print('hello')",
        language=Submission.Language.PYTHON,
    )


# ---------------------------------------------------------------------------
# Create tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestSubmissionCreate:
    @patch("apps.submissions.views.push_to_judge_queue", return_value=True)
    def test_create_submission_returns_201(self, mock_queue, auth_client, problem):
        url = reverse("submissions-list")
        data = {
            "problem": problem.pk,
            "code": "print('hello')",
            "language": "python",
        }
        response = auth_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert "id" in response.data
        assert response.data["verdict"] is None
        assert response.data["status"] == "queued"

    @patch("apps.submissions.views.push_to_judge_queue", return_value=True)
    def test_submission_pushed_to_queue(self, mock_queue, auth_client, problem):
        url = reverse("submissions-list")
        data = {"problem": problem.pk, "code": "x=1", "language": "python"}
        auth_client.post(url, data, format="json")
        mock_queue.assert_called_once()

    @patch("apps.submissions.views.push_to_judge_queue", return_value=False)
    def test_queue_error_still_returns_201(self, mock_queue, auth_client, problem):
        url = reverse("submissions-list")
        data = {"problem": problem.pk, "code": "x=1", "language": "python"}
        response = auth_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["status"] == "queue_error"


@pytest.mark.django_db
def test_submission_str_includes_pending_and_verdict(submission):
    # Covers Submission.__str__ branches (Pending vs verdict code).
    assert "Pending" in str(submission)

    submission.verdict = Submission.Verdict.AC
    submission.save(update_fields=["verdict"])
    assert "AC" in str(submission)

    def test_unauthenticated_cannot_submit(self, api_client, problem):
        url = reverse("submissions-list")
        data = {"problem": problem.pk, "code": "x=1", "language": "python"}
        response = api_client.post(url, data, format="json")
        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ]

    @patch("apps.submissions.views.push_to_judge_queue", return_value=True)
    def test_submit_with_active_contest(
        self, mock_queue, auth_client, problem, active_contest
    ):
        url = reverse("submissions-list")
        data = {
            "problem": problem.pk,
            "contest": active_contest.pk,
            "code": "x=1",
            "language": "python",
        }
        response = auth_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED

    def test_submit_with_finished_contest_returns_400(
        self, auth_client, problem, finished_contest
    ):
        url = reverse("submissions-list")
        data = {
            "problem": problem.pk,
            "contest": finished_contest.pk,
            "code": "x=1",
            "language": "python",
        }
        response = auth_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_problem_not_in_contest_returns_400(self, auth_client, active_contest):
        # Create a problem NOT added to the contest
        other_problem = Problem.objects.create(
            title="Other",
            description="",
            difficulty="easy",
            time_limit=1000,
            memory_limit=256,
        )
        url = reverse("submissions-list")
        data = {
            "problem": other_problem.pk,
            "contest": active_contest.pk,
            "code": "x=1",
            "language": "python",
        }
        response = auth_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ---------------------------------------------------------------------------
# List / retrieve tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestSubmissionList:
    def test_user_sees_own_submissions(self, auth_client, submission):
        url = reverse("submissions-list")
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        results = response.data.get("results", response.data)
        assert len(results) == 1
        assert results[0]["id"] == submission.pk

    def test_user_cannot_see_other_submissions(
        self, api_client, other_user, submission
    ):
        api_client.force_authenticate(user=other_user)
        url = reverse("submissions-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        results = response.data.get("results", response.data)
        assert len(results) == 0

    def test_retrieve_own_submission(self, auth_client, submission):
        url = reverse("submissions-detail", args=[submission.pk])
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == submission.pk

    def test_retrieve_other_submission_returns_404(
        self, api_client, other_user, submission
    ):
        api_client.force_authenticate(user=other_user)
        url = reverse("submissions-detail", args=[submission.pk])
        response = api_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


# ---------------------------------------------------------------------------
# No update / delete tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestSubmissionNoMutate:
    def test_update_not_allowed(self, auth_client, submission):
        url = reverse("submissions-detail", args=[submission.pk])
        response = auth_client.patch(url, {"code": "hacked"}, format="json")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_delete_not_allowed(self, auth_client, submission):
        url = reverse("submissions-detail", args=[submission.pk])
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


# ---------------------------------------------------------------------------
# Verdict tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestSubmissionVerdict:
    def test_verdict_is_null_on_create(self, submission):
        assert submission.verdict is None

    def test_is_pending_true_when_no_verdict(self, auth_client, submission):
        url = reverse("submissions-detail", args=[submission.pk])
        response = auth_client.get(url)
        assert response.data["is_pending"] is True

    def test_is_pending_false_after_verdict(self, auth_client, submission):
        submission.verdict = Submission.Verdict.AC
        submission.save()
        url = reverse("submissions-detail", args=[submission.pk])
        response = auth_client.get(url)
        assert response.data["is_pending"] is False
