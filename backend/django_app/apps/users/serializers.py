import io
from pathlib import Path

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image, ImageOps, UnidentifiedImageError
from rest_framework import serializers

from .models import User

# Avatar upload constants
MAX_AVATAR_SIZE_BYTES = 5 * 1024 * 1024
MAX_AVATAR_DIM_PX = 1024
AVATAR_OUTPUT_FORMAT = "WEBP"
AVATAR_OUTPUT_EXT = ".webp"
AVATAR_OUTPUT_CONTENT_TYPE = "image/webp"
AVATAR_OUTPUT_QUALITY = 85
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}


class UserRegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "password2"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username already exists")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email already exists")
        return value

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, verified_data):
        verified_data.pop("password2")
        user = User.objects.create_user(**verified_data)
        return user


class AvatarUploadSerializer(serializers.ModelSerializer):
    """Validates and saves an avatar image for the authenticated user."""

    class Meta:
        model = User
        fields = ("avatar",)

    def validate_avatar(self, value):
        if value.size > MAX_AVATAR_SIZE_BYTES:
            raise serializers.ValidationError(
                f"Image too large. Maximum size is "
                f"{MAX_AVATAR_SIZE_BYTES // (1024 * 1024)} MB."
            )
        content_type = getattr(value, "content_type", None)
        if content_type and content_type not in ALLOWED_CONTENT_TYPES:
            raise serializers.ValidationError(
                f"Unsupported image type '{content_type}'. "
                f"Allowed: {', '.join(ALLOWED_CONTENT_TYPES)}."
            )
        try:
            value.seek(0)
            image = Image.open(value)
            image.verify()
        except (UnidentifiedImageError, OSError, ValueError) as exc:
            raise serializers.ValidationError("Invalid image file.") from exc
        value.seek(0)
        image = Image.open(value)
        image = ImageOps.exif_transpose(image)
        if image.mode in {"P", "LA"}:
            image = image.convert("RGBA")
        elif image.mode not in {"RGB", "RGBA"}:
            image = image.convert("RGB")

        image.thumbnail(
            (MAX_AVATAR_DIM_PX, MAX_AVATAR_DIM_PX), Image.Resampling.LANCZOS
        )

        output = io.BytesIO()
        image.save(output, format=AVATAR_OUTPUT_FORMAT, quality=AVATAR_OUTPUT_QUALITY)
        output.seek(0)
        processed = SimpleUploadedFile(
            name=f"{Path(value.name).stem}{AVATAR_OUTPUT_EXT}",
            content=output.read(),
            content_type=AVATAR_OUTPUT_CONTENT_TYPE,
        )
        if processed.size > MAX_AVATAR_SIZE_BYTES:
            raise serializers.ValidationError(
                f"Image too large after processing. "
                f"Maximum size is {MAX_AVATAR_SIZE_BYTES // (1024 * 1024)} MB."
            )
        return processed
