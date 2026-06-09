from datetime import timedelta

import pytest
from allauth.socialaccount.models import SocialAccount
from apps.contests.models import Contest
from apps.users.models import EloHistory
from apps.users.services import calculate_elo
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user_data():
    return {
        "username": "testuser",
        "email": "test@mail.com",
        "password": "testpass123",
    }


@pytest.mark.django_db
def test_register_success(client, user_data):
    response = client.post("/api/users/register/", user_data, format="json")
    assert response.status_code == 201
    assert "access" in response.data
    assert "refresh" in response.data


@pytest.mark.django_db
def test_register_duplicate_email(client, user_data):
    client.post("/api/users/register/", user_data, format="json")
    response = client.post("/api/users/register/", user_data, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_login_success(client, user_data):
    client.post("/api/users/register/", user_data, format="json")
    response = client.post(
        "/api/users/login/",
        {"username": "testuser", "password": "testpass123"},
        format="json",
    )
    assert response.status_code == 200
    assert "access" in response.data


@pytest.mark.django_db
def test_register_duplicate_username(client, user_data):
    client.post("/api/users/register/", user_data, format="json")
    user_data["email"] = "other@mail.com"
    response = client.post("/api/users/register/", user_data, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_register_invalid_email(client, user_data):
    user_data["email"] = "notanemail"
    response = client.post("/api/users/register/", user_data, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_login_wrong_password(client, user_data):
    client.post("/api/users/register/", user_data, format="json")
    response = client.post(
        "/api/users/login/",
        {"username": "testuser", "password": "wrongpassword"},
        format="json",
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_login_nonexistent_user(client):
    response = client.post(
        "/api/users/login/",
        {"username": "nobody", "password": "testpass123"},
        format="json",
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_register_missing_fields(client):
    response = client.post("/api/users/register/", {}, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_token_refresh(client, user_data):
    client.post("/api/users/register/", user_data, format="json")
    login = client.post(
        "/api/users/login/",
        {"username": "testuser", "password": "testpass123"},
        format="json",
    )
    refresh = login.data["refresh"]
    response = client.post(
        "/api/users/token/refresh/",
        {"refresh": refresh},
        format="json",
    )
    assert response.status_code == 200
    assert "access" in response.data


@pytest.mark.django_db
def test_token_refresh_invalid(client):
    response = client.post(
        "/api/users/token/refresh/",
        {"refresh": "wrong_refresh"},
        format="json",
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_logout_success(client, user_data):
    client.post("/api/users/register/", user_data, format="json")

    login = client.post(
        "/api/users/login/",
        {"username": "testuser", "password": "testpass123"},
        format="json",
    )

    refresh = login.data["refresh"]
    access = login.data["access"]

    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {access}"
    )

    response = client.post(
        "/api/users/logout/",
        {"refresh": refresh},
        format="json",
    )

    assert response.status_code == 205


@pytest.mark.django_db
def test_logout_invalid_token(client):
    response = client.post(
        "/api/users/logout/", {"refresh": "wrong_refresh"}, format="json"
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_logout_without_token(client):
    response = client.post(
        "/api/users/logout/",
        {},
        format="json",
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_github_callback_returns_jwt_for_authenticated_user(client):
    user = User.objects.create_user(
        username="github_user",
        email="github@example.com",
        password="pass",
    )
    client.force_authenticate(user=user)

    response = client.get("/api/users/github/callback/")

    assert response.status_code == 200
    assert response.data["access"]
    assert response.data["refresh"]
    assert response.data["user"] == {
        "id": user.id,
        "username": user.username,
        "email": user.email,
    }


@pytest.mark.django_db
def test_github_callback_unauthenticated_user(client):
    response = client.get("/api/users/github/callback/")

    assert response.status_code in [401, 403]
    assert "access" not in response.data
    assert "refresh" not in response.data


@pytest.mark.django_db
def test_repeated_github_login_uses_existing_social_account(client):
    user = User.objects.create_user(
        username="github_user",
        email="github@example.com",
        password="pass",
    )
    SocialAccount.objects.create(
        user=user,
        provider="github",
        uid="github-123",
        extra_data={"login": "github_user"},
    )

    social_account = SocialAccount.objects.get(provider="github", uid="github-123")
    client.force_authenticate(user=social_account.user)
    response = client.get("/api/users/github/callback/")

    assert response.status_code == 200
    assert User.objects.count() == 1
    assert response.data["user"]["id"] == user.id


@pytest.mark.django_db
def test_github_user_is_linked_by_social_account_uid():
    user = User.objects.create_user(
        username="github_user",
        email="github@example.com",
        password="pass",
    )

    social_account = SocialAccount.objects.create(
        user=user,
        provider="github",
        uid="github-123",
        extra_data={"login": "github_user"},
    )

    assert social_account.user == user
    assert social_account.provider == "github"
    assert social_account.uid == "github-123"


class EloRatingTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="qwerty",
            email="p1@test.com",
            password="123wehfiew123",
            elo_rating=1200,
        )
        self.user2 = User.objects.create_user(
            username="asdfg",
            email="p2@test.com",
            password="ioehfuihwe128343",
            elo_rating=1200,
        )

        start = timezone.now()
        end = start + timedelta(hours=2)

        self.contest = Contest.objects.create(
            title="Test Match", start_time=start, end_time=end, status="pending"
        )

        self.contest.participants.add(self.user1, self.user2)

        self.first_player = self.user1
        self.second_player = self.user2
        self.match = self.contest
        self.winner = self.user1
        self.loser = self.user2

    def test_equal_players_match(self):
        calculate_elo(
            winner=self.first_player, loser=self.second_player, contest=self.match
        )
        self.winner.refresh_from_db()
        self.second_player.refresh_from_db()  # Фиксим: обязательно обновляем из базы!

        self.assertEqual(self.winner.elo_rating, 1216)
        self.assertEqual(self.second_player.elo_rating, 1184)

    def test_upset_match(self):
        self.first_player.elo_rating = 1000
        self.second_player.elo_rating = 1600
        self.first_player.save()
        self.second_player.save()

        calculate_elo(
            winner=self.first_player, loser=self.second_player, contest=self.contest
        )
        self.first_player.refresh_from_db()

        self.assertTrue(self.first_player.elo_rating > 1030)

    def test_history_logging(self):
        calculate_elo(
            winner=self.first_player, loser=self.second_player, contest=self.contest
        )

        self.assertEqual(EloHistory.objects.count(), 2)

        win_hist = EloHistory.objects.get(user=self.first_player)
        self.assertEqual(win_hist.old_rating, 1200)
        self.assertEqual(win_hist.new_rating, 1216)
        self.assertEqual(win_hist.delta, 16)

        loss_hist = EloHistory.objects.get(user=self.second_player)
        self.assertEqual(loss_hist.old_rating, 1200)
        self.assertEqual(loss_hist.new_rating, 1184)
        self.assertEqual(loss_hist.delta, -16)

    def test_calculate_elo_success(self):
        self.user1.elo_rating = 1000
        self.user2.elo_rating = 1000

        self.user1.save()
        self.user2.save()

        old_winner_rating = self.user1.elo_rating
        old_loser_rating = self.user2.elo_rating

        calculate_elo(winner=self.user1, loser=self.user2, contest=self.contest)

        self.user1.refresh_from_db()
        self.user2.refresh_from_db()

        self.assertTrue(self.user1.elo_rating > old_winner_rating)
        self.assertTrue(self.user2.elo_rating < old_loser_rating)

        history_count = EloHistory.objects.filter(contest=self.contest).count()
        self.assertEqual(history_count, 2)

        winner_history = EloHistory.objects.filter(
            user=self.user1, contest=self.contest
        ).first()
        loser_history = EloHistory.objects.filter(
            user=self.user2, contest=self.contest
        ).first()

        self.assertIsNotNone(winner_history)
        self.assertIsNotNone(loser_history)

        self.assertEqual(winner_history.old_rating, old_winner_rating)
        self.assertEqual(winner_history.new_rating, self.user1.elo_rating)
        self.assertEqual(
            winner_history.delta, self.user1.elo_rating - old_winner_rating
        )
        self.assertTrue(winner_history.delta > 0)

        self.assertEqual(loser_history.old_rating, old_loser_rating)
        self.assertEqual(loser_history.new_rating, self.user2.elo_rating)
        self.assertEqual(loser_history.delta, self.user2.elo_rating - old_loser_rating)
        self.assertTrue(loser_history.delta < 0)

        self.assertTrue(len(str(winner_history)) > 0)
