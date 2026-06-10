from rest_framework import serializers

from .models import Submission


class SubmissionCreateSerializer(serializers.ModelSerializer):
    """Used for POST /api/submissions/ — accepts code, language, problem, contest."""

    class Meta:
        model = Submission
        fields = ["id", "problem", "contest", "code", "language"]

    def validate(self, attrs):
        contest = attrs.get("contest")
        problem = attrs.get("problem")

        # If contest is provided — problem must belong to that contest
        if contest and not contest.problems.filter(pk=problem.pk).exists():
            raise serializers.ValidationError(
                {"problem": "This problem is not part of the specified contest."}
            )

        # Contest must be active to submit
        if contest:
            contest.update_status()
            from apps.contests.models import Contest

            if contest.status != Contest.Status.ACTIVE:
                raise serializers.ValidationError(
                    {"contest": "You can only submit during an active contest."}
                )

        return attrs

    def create(self, validated_data):
        # User is injected from the view
        return Submission.objects.create(**validated_data)


class SubmissionSerializer(serializers.ModelSerializer):
    """Used for GET — read-only, full info."""

    verdict_display = serializers.CharField(
        source="get_verdict_display", read_only=True
    )
    language_display = serializers.CharField(
        source="get_language_display", read_only=True
    )
    is_pending = serializers.SerializerMethodField()

    class Meta:
        model = Submission
        fields = [
            "id",
            "user",
            "problem",
            "contest",
            "code",
            "language",
            "language_display",
            "verdict",
            "verdict_display",
            "is_pending",
            "execution_time_ms",
            "memory_used_mb",
            "created_at",
        ]
        read_only_fields = fields

    def get_is_pending(self, obj):
        return obj.verdict is None
