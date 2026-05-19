from rest_framework import mixins, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Submission
from .serializers import SubmissionCreateSerializer, SubmissionSerializer
from .tasks import push_to_judge_queue


class SubmissionViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    Submissions — create and read only (no update, no delete).

    POST   /api/submissions/        — create submission, send to judge queue
    GET    /api/submissions/        — list own submissions
    GET    /api/submissions/{id}/   — retrieve own submission
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Users can only see their own submissions
        return (
            Submission.objects.select_related("problem", "contest")
            .filter(user=self.request.user)
            .order_by("-created_at")
        )

    def get_serializer_class(self):
        if self.action == "create":
            return SubmissionCreateSerializer
        return SubmissionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Inject current user
        submission = serializer.save(user=request.user)

        # Push to Redis judge queue
        queued = push_to_judge_queue(submission)

        return Response(
            {
                "id": submission.pk,
                "status": "queued" if queued else "queue_error",
                "verdict": submission.verdict,  # None at this point
                "created_at": submission.created_at,
            },
            status=status.HTTP_201_CREATED,
        )
