import logging

from django.utils import timezone

from celery import shared_task

from .models import Contest


logger = logging.getLogger(__name__)


@shared_task
def update_contest_statuses() -> dict:
    """
    Periodic task: update contest statuses based on start/end times.

    Returns a small summary dict for logging/inspection.
    """

    now = timezone.now()

    # Finished: any contest whose end_time has passed should be finished.
    finished = Contest.objects.filter(end_time__lt=now).exclude(
        status=Contest.Status.FINISHED
    )
    finished_updated = finished.update(status=Contest.Status.FINISHED, updated_at=now)

    # Active: start_time <= now <= end_time
    active = Contest.objects.filter(start_time__lte=now, end_time__gte=now).exclude(
        status=Contest.Status.ACTIVE
    )
    active_updated = active.update(status=Contest.Status.ACTIVE, updated_at=now)

    # Pending: start_time in future
    pending = Contest.objects.filter(start_time__gt=now).exclude(
        status=Contest.Status.PENDING
    )
    pending_updated = pending.update(status=Contest.Status.PENDING, updated_at=now)

    summary = {
        "updated": {
            "finished": finished_updated,
            "active": active_updated,
            "pending": pending_updated,
        },
        "total_current": {
            "finished": Contest.objects.filter(status=Contest.Status.FINISHED).count(),
            "active": Contest.objects.filter(status=Contest.Status.ACTIVE).count(),
            "pending": Contest.objects.filter(status=Contest.Status.PENDING).count(),
        },
    }


    logger.info(
        "update_contest_statuses updated=%s total=%s",
        summary["updated"],
        summary["total_current"],
    )

    return summary
