import json
from datetime import timedelta

from apps.contests.models import Contest
from apps.submissions.models import Submission
from apps.users.models import EloHistory, User
from apps.users.services import calculate_elo
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from sorl.thumbnail import get_thumbnail

from .serializers import (
    AvatarUploadSerializer,
    EloHistorySerializer,
    UserRegisterSerializer,
    UserSerializer,
)

ACTIVITY_WINDOW_DAYS = 365


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "user": serializer.data,
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AvatarUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = AvatarUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.avatar = serializer.validated_data["avatar"]
        user.save(update_fields=["avatar"])
        thumb_128 = get_thumbnail(user.avatar, "128x128", crop="center", quality=85)
        thumb_256 = get_thumbnail(user.avatar, "256x256", crop="center", quality=85)

        return Response(
            {
                "avatar": user.avatar.url,
                "thumbnails": {
                    "128": thumb_128.url,
                    "256": thumb_256.url,
                },
            }
        )


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)

        except KeyError:
            return Response(
                {"error": "Refresh token required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except TokenError:
            return Response(
                {"error": "Invalid token"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserActivityView(APIView):
    """
    Per-day submission counts for a user's activity heatmap (GitHub-style).

    GET /api/users/{id}/activity/ -> sparse map of ISO date -> submission count
    for the last ACTIVITY_WINDOW_DAYS days, e.g. {"2026-05-01": 3, "2026-05-02": 7}.

    Counts ALL submissions regardless of verdict (activity, not achievement).
    Requires auth (project default); 404 if the user does not exist.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, user_id: int):
        get_object_or_404(User, pk=user_id)
        since = timezone.now() - timedelta(days=ACTIVITY_WINDOW_DAYS)
        rows = (
            Submission.objects.filter(user_id=user_id, created_at__gte=since)
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )
        # Sparse: only days that actually have submissions are returned.
        data = {row["day"].isoformat(): row["count"] for row in rows}
        return Response(data)


class UserEloHistoryView(APIView):
    """
    ELO rating change history for a user, for a Dashboard rating sparkline.

    GET /api/users/{username}/elo-history/ -> list of ELO changes oldest-first
    (chronological), so the frontend can plot the rating over time directly.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, username: str):
        user = get_object_or_404(User, username=username)
        history = EloHistory.objects.filter(user=user).order_by("created_at")
        return Response(EloHistorySerializer(history, many=True).data)


class UserDetailView(RetrieveAPIView):
    """GET /api/users/{username}/ — public profile incl. rank from elo_rating."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "username"
    lookup_url_kwarg = "username"


def finish_contest_view(request, contest_id):
    contest = get_object_or_404(Contest, id=contest_id)

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            winner_id = data.get("winner_id")
            loser_id = data.get("loser_id")
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    else:
        winner_id = request.GET.get("winner_id")
        loser_id = request.GET.get("loser_id")

    if not winner_id or not loser_id:
        return JsonResponse({"error": "Missing winner_id or loser_id"}, status=400)

    user_winner = get_object_or_404(User, id=winner_id)
    user_loser = get_object_or_404(User, id=loser_id)

    calculate_elo(winner=user_winner, loser=user_loser, contest=contest)

    return JsonResponse({"status": "success"})
