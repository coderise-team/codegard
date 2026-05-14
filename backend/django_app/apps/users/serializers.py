from rest_framework import serializers


from .models import User

# Maximum allowed upload size: 5 MB
MAX_AVATAR_SIZE_BYTES = 5 * 1024 * 1024
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}


class AvatarUploadSerializer(serializers.ModelSerializer):
    """Validates and saves an avatar image for the authenticated user."""

    class Meta:
        model = User
        fields = ("avatar",)

    def validate_avatar(self, value):
        if value.size > MAX_AVATAR_SIZE_BYTES:
            raise serializers.ValidationError(
                f"Image too large. Maximum size is {MAX_AVATAR_SIZE_BYTES // (1024 * 1024)} MB."
            )
        content_type = getattr(value, "content_type", None)
        if content_type and content_type not in ALLOWED_CONTENT_TYPES:
            raise serializers.ValidationError(
                f"Unsupported image type '{content_type}'. "
                f"Allowed: {', '.join(ALLOWED_CONTENT_TYPES)}."
            )
        return value
