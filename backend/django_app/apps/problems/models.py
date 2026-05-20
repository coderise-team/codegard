from django.db import models


class Problem(models.Model):
    class Difficulty(models.TextChoices):
        EASY = "easy", "Easy"
        MEDIUM = "medium", "Medium"
        HARD = "hard", "Hard"

    title = models.CharField(max_length=255)
    description = models.TextField()
    difficulty = models.CharField(
        max_length=10,
        choices=Difficulty.choices,
        default=Difficulty.EASY,
    )
    time_limit = models.PositiveIntegerField(
        help_text="Time limit in milliseconds",
        default=1000,
    )
    memory_limit = models.PositiveIntegerField(
        help_text="Memory limit in megabytes",
        default=256,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.difficulty})"


class TestCase(models.Model):
    __test__ = False

    problem = models.ForeignKey(
        Problem,
        on_delete=models.CASCADE,
        related_name="test_cases",
    )
    input = models.TextField()
    expected_output = models.TextField()
    is_hidden = models.BooleanField(
        default=False,
        help_text="Hidden test cases are only used by the judge, not shown to users.",
    )

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"TestCase #{self.pk} for '{self.problem.title}'"
