from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from sorl.thumbnail import get_thumbnail

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (("Profile", {"fields": ("avatar",)}),)

    def save_model(self, request, obj, form, change):
        """
        When an avatar is uploaded via admin, generate thumbnails immediately
        so they appear in R2 under `media/thumbnails/...`.
        """

        super().save_model(request, obj, form, change)
        if "avatar" in getattr(form, "changed_data", []):
            try:
                if obj.avatar:
                    get_thumbnail(obj.avatar, "128x128", crop="center", quality=85)
                    get_thumbnail(obj.avatar, "256x256", crop="center", quality=85)
            except Exception:
                # Don't block saving the user if thumbnail upload fails.
                pass
