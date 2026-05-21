from datetime import timedelta

import pytest
from apps.contests.models import Contest
from apps.realtime.routing import websocket_urlpatterns
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.utils import timezone


def make_app():
    return URLRouter(websocket_urlpatterns)


def make_communicator(user, contest_id):
    app = make_app()
    communicator = WebsocketCommunicator(app, f"/ws/contests/{contest_id}/")
    communicator.scope["user"] = user
    return communicator


async def add_participant(contest, user) -> None:
    await database_sync_to_async(contest.participants.add)(user)


@pytest.fixture
def active_contest(db):
    now = timezone.now()
    contest = Contest.objects.create(
        title="Test Contest",
        start_time=now - timedelta(hours=1),
        end_time=now + timedelta(hours=2),
    )
    return contest


@pytest.fixture
def user(db, django_user_model):
    return django_user_model.objects.create_user(username="player1", password="pass")


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_unauthenticated_user_is_rejected(active_contest):
    from django.contrib.auth.models import AnonymousUser

    app = make_app()
    communicator = WebsocketCommunicator(app, f"/ws/contests/{active_contest.pk}/")
    communicator.scope["user"] = AnonymousUser()
    connected, code = await communicator.connect()
    assert not connected
    assert code == 4001


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_nonexistent_contest_is_rejected(user):
    communicator = make_communicator(user, contest_id=99999)
    connected, code = await communicator.connect()
    assert not connected
    assert code == 4004


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_non_participant_is_rejected(user, active_contest):
    communicator = make_communicator(user, active_contest.pk)
    connected, code = await communicator.connect()
    assert not connected
    assert code == 4003


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_connect_sends_initial_leaderboard(user, active_contest):
    await add_participant(active_contest, user)
    communicator = make_communicator(user, active_contest.pk)
    try:
        connected, _ = await communicator.connect()
        assert connected

        response = await communicator.receive_json_from()
        assert response["type"] == "leaderboard_update"
        assert "leaderboard" in response
    finally:
        await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_leaderboard_update_forwarded(user, active_contest):
    await add_participant(active_contest, user)
    communicator = make_communicator(user, active_contest.pk)
    try:
        await communicator.connect()
        await communicator.receive_json_from()  # consume initial

        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            f"contest_{active_contest.pk}",
            {"type": "leaderboard_update", "leaderboard": [{"rank": 1}]},
        )

        response = await communicator.receive_json_from()
        assert response["type"] == "leaderboard_update"
        assert response["leaderboard"] == [{"rank": 1}]
    finally:
        await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_problem_solved_notification(user, active_contest):
    await add_participant(active_contest, user)
    communicator = make_communicator(user, active_contest.pk)
    try:
        await communicator.connect()
        await communicator.receive_json_from()  # consume initial

        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            f"contest_{active_contest.pk}",
            {
                "type": "problem_solved",
                "username": "opponent",
                "problem_title": "Two Sum",
            },
        )

        response = await communicator.receive_json_from()
        assert response["type"] == "problem_solved"
        assert response["username"] == "opponent"
        assert response["problem_title"] == "Two Sum"
    finally:
        await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_contest_ended_closes_connection(user, active_contest):
    await add_participant(active_contest, user)
    communicator = make_communicator(user, active_contest.pk)
    try:
        await communicator.connect()
        await communicator.receive_json_from()  # consume initial

        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            f"contest_{active_contest.pk}",
            {"type": "contest_ended"},
        )

        response = await communicator.receive_json_from()
        assert response["type"] == "contest_ended"
    finally:
        await communicator.disconnect()
