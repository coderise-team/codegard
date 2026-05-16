from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from sorl.thumbnail import get_thumbnail

from .serializers import AvatarUploadSerializer


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