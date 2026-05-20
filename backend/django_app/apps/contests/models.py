from django.db import models
from django.utils import timezone


class Contest(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACTIVE = "active", "Active"
        FINISHED = "finished", "Finished"

    title = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    problems = models.ManyToManyField(
        "problems.Problem",
        blank=True,
        related_name="contests",
    )
    participants = models.ManyToManyField(
        "users.User",
        blank=True,
        related_name="contests",
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_time"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(end_time__gt=models.F("start_time")),
                name="check_start_before_end",
            )
        ]

    def __str__(self):
        return f"{self.title} ({self.status})"

    def _compute_status(self, now):
        if now < self.start_time:
            return self.Status.PENDING
        if self.start_time <= now <= self.end_time:
            return self.Status.ACTIVE
        return self.Status.FINISHED

    def save(self, *args, **kwargs):
        # Ensure status is consistent at creation/update time.
        if self.start_time and self.end_time:
            self.status = self._compute_status(timezone.now())
        super().save(*args, **kwargs)

    def update_status(self):
        """Recalculate and save status based on current time."""
        new_status = self._compute_status(timezone.now())

        if self.status != new_status:
            self.status = new_status
            self.save(update_fields=["status"])
