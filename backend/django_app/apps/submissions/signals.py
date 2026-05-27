from apps.contests.services import calculate_score
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Submission


@receiver(pre_save, sender=Submission)
def _capture_previous_verdict(sender, instance: Submission, **kwargs):
    if not instance.pk:
        instance._previous_verdict = None
        return
    instance._previous_verdict = (
        Submission.objects.filter(pk=instance.pk)
        .values_list("verdict", flat=True)
        .first()
    )


@receiver(post_save, sender=Submission)
def _recalculate_contest_score_on_ac(
    sender, instance: Submission, created: bool, **kwargs
):
    if not instance.contest:
        return
    if instance.verdict != Submission.Verdict.AC:
        return

    previous_verdict = getattr(instance, "_previous_verdict", None)
    if not created and previous_verdict == Submission.Verdict.AC:
        return

    calculate_score(instance.user, instance.contest)
    _broadcast_problem_solved(instance)
    _broadcast_leaderboard(instance.contest)


@receiver(post_save, sender=Submission)
def _broadcast_verdict_update(sender, instance: Submission, **kwargs):
    if instance.verdict is None:
        return
    previous_verdict = getattr(instance, "_previous_verdict", None)
    if previous_verdict == instance.verdict:
        return
    _broadcast_submission_update(instance)


def _broadcast_submission_update(submission: Submission) -> None:
    from asgiref.sync import async_to_sync
    from channels.layers import get_channel_layer

    channel_layer = get_channel_layer()
    if channel_layer is None:
        return

    async_to_sync(channel_layer.group_send)(
        f"submission_{submission.pk}",
        {
            "type": "submission_update",
            "submission_id": submission.pk,
            "verdict": submission.verdict,
        },
    )


def _broadcast_leaderboard(contest):
    from apps.contests.serializers import LeaderboardEntrySerializer
    from apps.contests.services import get_leaderboard
    from asgiref.sync import async_to_sync
    from channels.layers import get_channel_layer

    channel_layer = get_channel_layer()
    if channel_layer is None:
        return

    entries = list(get_leaderboard(contest))
    for rank, entry in enumerate(entries, start=1):
        entry.rank = rank
    data = list(LeaderboardEntrySerializer(entries, many=True).data)

    async_to_sync(channel_layer.group_send)(
        f"contest_{contest.pk}",
        {"type": "leaderboard_update", "leaderboard": data},
    )


def _broadcast_problem_solved(submission: Submission) -> None:
    from asgiref.sync import async_to_sync
    from channels.layers import get_channel_layer

    channel_layer = get_channel_layer()
    if channel_layer is None:
        return

    async_to_sync(channel_layer.group_send)(
        f"contest_{submission.contest_id}",
        {
            "type": "problem_solved",
            "username": submission.user.username,
            "problem_title": submission.problem.title,
        },
    )
