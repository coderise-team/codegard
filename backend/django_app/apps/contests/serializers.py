from apps.problems.models import Problem
from rest_framework import serializers

from .models import Contest


class ContestProblemSerializer(serializers.ModelSerializer):
    """
    Problem serializer for contest context.

    Important: does NOT include test cases (hidden or visible).
    """

    class Meta:
        model = Problem
        fields = [
            "id",
            "title",
            "description",
            "difficulty",
            "time_limit",
            "memory_limit",
        ]


class ContestSerializer(serializers.ModelSerializer):
    """Read serializer — used for list and retrieve."""

    problems_count = serializers.SerializerMethodField()
    participants_count = serializers.SerializerMethodField()
    is_joined = serializers.SerializerMethodField()

    class Meta:
        model = Contest
        fields = [
            "id",
            "title",
            "start_time",
            "end_time",
            "status",
            "problems_count",
            "participants_count",
            "is_joined",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["status", "created_at", "updated_at"]

    def get_problems_count(self, obj):
        if hasattr(obj, "problems_count_annotated"):
            return obj.problems_count_annotated
        return obj.problems.count()

    def get_participants_count(self, obj):
        if hasattr(obj, "participants_count_annotated"):
            return obj.participants_count_annotated
        return obj.participants.count()

    def get_is_joined(self, obj):
        if hasattr(obj, "is_joined_annotated"):
            return obj.is_joined_annotated

        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            return obj.participants.filter(pk=request.user.pk).exists()
        return False


class ContestDetailSerializer(ContestSerializer):
    """Retrieve serializer — includes full problem list."""

    problems = ContestProblemSerializer(many=True, read_only=True)

    class Meta(ContestSerializer.Meta):
        fields = ContestSerializer.Meta.fields + ["problems"]


class ContestWriteSerializer(serializers.ModelSerializer):
    """Create / update serializer."""

    class Meta:
        model = Contest
        fields = [
            "id",
            "title",
            "start_time",
            "end_time",
            "problems",
        ]

    def validate(self, attrs):
        start = attrs.get("start_time") or getattr(self.instance, "start_time", None)
        end = attrs.get("end_time") or getattr(self.instance, "end_time", None)

        if start and end and end <= start:
            raise serializers.ValidationError(
                {"end_time": "end_time must be after start_time."}
            )
        return attrs
