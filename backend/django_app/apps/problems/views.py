from apps.submissions.models import Submission
from django.db.models import Count, Q
from rest_framework import filters, viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly

from .models import Problem
from .serializers import ProblemSerializer, ProblemWriteSerializer


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
