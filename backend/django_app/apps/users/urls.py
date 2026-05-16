from django.urls import path

from .views import AvatarUploadView

app_name = "users"

urlpatterns = [
    path("avatar/", AvatarUploadView.as_view(), name="avatar-upload"),
]
