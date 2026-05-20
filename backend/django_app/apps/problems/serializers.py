from rest_framework import serializers

from .models import Problem, TestCase


class TestCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCase
        fields = ["id", "input", "expected_output", "is_hidden"]


class TestCasePublicSerializer(serializers.ModelSerializer):
    """Serializer for regular users — hides is_hidden test cases."""

    class Meta:
        model = TestCase
        fields = ["id", "input", "expected_output"]


class ProblemSerializer(serializers.ModelSerializer):
    """List / retrieve serializer — shows only visible test cases to regular users."""

    test_cases = serializers.SerializerMethodField()

    class Meta:
        model = Problem
        fields = [
            "id",
            "title",
            "description",
            "difficulty",
            "time_limit",
            "memory_limit",
            "test_cases",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def get_test_cases(self, obj):
        request = self.context.get("request")
        is_staff = request and request.user and request.user.is_staff

        if is_staff:
            # Staff sees all test cases including hidden
            qs = obj.test_cases.all()
            return TestCaseSerializer(qs, many=True).data
        else:
            # Regular users only see visible test cases
            qs = obj.test_cases.filter(is_hidden=False)
            return TestCasePublicSerializer(qs, many=True).data


class ProblemWriteSerializer(serializers.ModelSerializer):
    """Create / update serializer — accepts test_cases as nested input."""

    test_cases = TestCaseSerializer(many=True, required=False)

    class Meta:
        model = Problem
        fields = [
            "id",
            "title",
            "description",
            "difficulty",
            "time_limit",
            "memory_limit",
            "test_cases",
        ]

    def create(self, validated_data):
        test_cases_data = validated_data.pop("test_cases", [])
        problem = Problem.objects.create(**validated_data)
        for tc in test_cases_data:
            TestCase.objects.create(problem=problem, **tc)
        return problem

    def update(self, instance, validated_data):
        test_cases_data = validated_data.pop("test_cases", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if test_cases_data is not None:
            instance.test_cases.all().delete()
            for tc in test_cases_data:
                TestCase.objects.create(problem=instance, **tc)

        return instance
