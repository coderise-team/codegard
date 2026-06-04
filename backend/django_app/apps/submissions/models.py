from django.conf import settings
from django.db import models
from schemas.request import LanguageEnum
from schemas.response import VerdictEnum


class Submission(models.Model):
    class Language(models.TextChoices):
        PYTHON = LanguageEnum.PYTHON.value, "Python"

    class Verdict(models.TextChoices):
        AC = VerdictEnum.AC.value, "Accepted"
        WA = VerdictEnum.WA.value, "Wrong Answer"
        TLE = VerdictEnum.TLE.value, "Time Limit Exceeded"
        MLE = VerdictEnum.MLE.value, "Memory Limit Exceeded"
        RE = VerdictEnum.RE.value, "Runtime Error"
        CE = VerdictEnum.CE.value, "Compilation Error"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="submissions",
    )
    problem = models.ForeignKey(
        "problems.Problem",
        on_delete=models.CASCADE,
        related_name="submissions",
    )
    contest = models.ForeignKey(
        "contests.Contest",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="submissions",
    )
    code = models.TextField()
    language = models.CharField(
        max_length=20,
        choices=Language.choices,
    )
    verdict = models.CharField(
        max_length=3,
        choices=Verdict.choices,
        null=True,
        blank=True,
        default=None,
        help_text="Null until judge processes the submission.",
    )
    execution_time_ms = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Execution time in milliseconds.",
    )
    memory_used_mb = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Memory used in megabytes.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        verdict = self.verdict or "Pending"
        return f"Submission #{self.pk} by {self.user} — {verdict}"
