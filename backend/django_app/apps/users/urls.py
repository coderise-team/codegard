from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    AvatarUploadView,
    LoginView,
    LogoutView,
    MeView,
    RegisterView,
    UserActivityView,
)

app_name = "users"

urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("login/", LoginView.as_view()),
    path("token/refresh/", TokenRefreshView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("avatar/", AvatarUploadView.as_view(), name="avatar-upload"),
    path("me/", MeView.as_view()),
    path("activity/<int:user_id>/", UserActivityView.as_view(), name="user-activity"),
]
