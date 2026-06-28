from apps.submissions.models import Submission
from django.db.models import Count, Q
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAdminUser,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response

from .models import Problem
from .serializers import (
    ProblemSerializer,
    ProblemWriteSerializer,
    RecommendedProblemSerializer,
)

RECOMMENDED_PER_DIFFICULTY = 2
RECOMMENDED_TOTAL = 6


class ProblemViewSet(viewsets.ModelViewSet):
    """
    CRUD for Problems.

    GET    /api/problems/          — list all problems (filter by ?difficulty=easy)
    POST   /api/problems/          — create problem (admin only)
    GET    /api/problems/{id}/     — retrieve problem with test cases
    PUT    /api/problems/{id}/     — update problem (admin only)
    PATCH  /api/problems/{id}/     — partial update (admin only)
    DELETE /api/problems/{id}/     — delete problem (admin only)
    """

    queryset = Problem.objects.prefetch_related("test_cases", "tags").all()
    filter_backends = [filters.SearchFilter]
    search_fields = ["title"]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminUser()]
        if self.action == "recommended":
            return [IsAuthenticated()]
        return [IsAuthenticatedOrReadOnly()]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ProblemWriteSerializer
        return ProblemSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        difficulty = self.request.query_params.get("difficulty")
        if difficulty in ["easy", "medium", "hard"]:
            queryset = queryset.filter(difficulty=difficulty)
        # Acceptance counters in one pass - both counts over the same 'submissions'
        # relation, so it's a single JOIN with no fan-out (no distinct needed).
        queryset = queryset.annotate(
            total_submissions=Count("submissions"),
            ac_submissions=Count(
                "submissions",
                filter=Q(submissions__verdict=Submission.Verdict.AC),
            ),
        )
        return queryset

    @action(detail=False, methods=["get"])
    def recommended(self, request):
        """Up to 6 unsolved problems for the current user: 2 random per
        difficulty, backfilled across difficulties, ordered easy -> hard.
        Unsolved = the user has no AC for the problem.
        """
        user = request.user

        solved_ids = (
            Submission.objects.filter(user=user, verdict=Submission.Verdict.AC)
            .values_list("problem", flat=True)
            .distinct()
        )

        unsolved = (
            Problem.objects.exclude(id__in=solved_ids)
            .prefetch_related("tags")
            .annotate(
                total_submissions=Count("submissions"),
                ac_submissions=Count(
                    "submissions",
                    filter=Q(submissions__verdict=Submission.Verdict.AC),
                ),
            )
        )

        picked = []
        picked_ids = set()
        for difficulty in ("easy", "medium", "hard"):
            chunk = list(
                unsolved.filter(difficulty=difficulty).order_by("?")[
                    :RECOMMENDED_PER_DIFFICULTY
                ]
            )
            picked.extend(chunk)
            picked_ids.update(p.id for p in chunk)

        shortfall = RECOMMENDED_TOTAL - len(picked)
        if shortfall > 0:
            picked.extend(unsolved.exclude(id__in=picked_ids).order_by("?")[:shortfall])

        difficulty_rank = {"easy": 0, "medium": 1, "hard": 2}
        picked.sort(key=lambda p: difficulty_rank[p.difficulty])
        serializer = RecommendedProblemSerializer(picked, many=True)
        return Response(serializer.data)
