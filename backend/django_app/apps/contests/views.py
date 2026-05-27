from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAdminUser,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response

from .models import Contest
from .serializers import (
    ContestDetailSerializer,
    ContestSerializer,
    ContestWriteSerializer,
    LeaderboardEntrySerializer,
)
from .services import get_leaderboard


class ContestViewSet(viewsets.ModelViewSet):
    """
    CRUD for Contests + join action.

    GET    /api/contests/              — list all contests
    POST   /api/contests/              — create contest (admin only)
    GET    /api/contests/{id}/         — retrieve contest with problems
    PUT    /api/contests/{id}/         — update contest (admin only)
    PATCH  /api/contests/{id}/         — partial update (admin only)
    DELETE /api/contests/{id}/         — delete contest (admin only)
    POST   /api/contests/{id}/join/    — join contest (authenticated users)
    POST   /api/contests/{id}/leave/   — leave contest (authenticated users)
    """

    queryset = Contest.objects.prefetch_related("problems").all()
    filter_backends = [filters.SearchFilter]
    search_fields = ["title"]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminUser()]
        if self.action in ["join", "leave"]:
            return [IsAuthenticated()]
        return [IsAuthenticatedOrReadOnly()]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ContestWriteSerializer
        if self.action == "retrieve":
            return ContestDetailSerializer
        return ContestSerializer

    def get_queryset(self):
        from django.db.models import Count, Exists, OuterRef

        queryset = super().get_queryset()

        # Filter by status
        status_filter = self.request.query_params.get("status")
        if status_filter in ["pending", "active", "finished"]:
            queryset = queryset.filter(status=status_filter)

        # Annotations to avoid N+1 queries
        queryset = queryset.annotate(
            participants_count_annotated=Count("participants", distinct=True),
            problems_count_annotated=Count("problems", distinct=True),
        )

        user = self.request.user
        if user and user.is_authenticated:
            # Check if user is in the M2M through table
            ThroughModel = Contest.participants.through
            user_joined = ThroughModel.objects.filter(
                contest_id=OuterRef("pk"), user_id=user.pk
            )
            queryset = queryset.annotate(is_joined_annotated=Exists(user_joined))

        return queryset.order_by("-start_time")

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def join(self, request, pk=None):
        """POST /api/contests/{id}/join/"""
        contest = self.get_object()
        contest.update_status()

        if contest.status == Contest.Status.FINISHED:
            return Response(
                {"detail": "Cannot join a finished contest."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if contest.participants.filter(pk=request.user.pk).exists():
            return Response(
                {"detail": "You have already joined this contest."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        contest.participants.add(request.user)
        return Response(
            {"detail": "Successfully joined the contest."},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def leave(self, request, pk=None):
        """POST /api/contests/{id}/leave/"""
        contest = self.get_object()

        if contest.status == Contest.Status.ACTIVE:
            return Response(
                {"detail": "Cannot leave an active contest."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not contest.participants.filter(pk=request.user.pk).exists():
            return Response(
                {"detail": "You are not a participant of this contest."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        contest.participants.remove(request.user)
        return Response(
            {"detail": "Successfully left the contest."},
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["get"],
        permission_classes=[IsAuthenticatedOrReadOnly],
    )
    def leaderboard(self, request, pk=None):
        """GET /api/contests/{id}/leaderboard/"""
        contest = self.get_object()
        entries = get_leaderboard(contest)

        # Inject rank number
        data = []
        for rank, entry in enumerate(entries, start=1):
            entry.rank = rank
            data.append(entry)

        serializer = LeaderboardEntrySerializer(data, many=True)
        return Response(serializer.data)
