from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    AvatarUploadView,
    LogoutView,
    RegisterView,
    UserActivityView,
    UserDetailView,
    UserEloHistoryView,
)

app_name = "users"

urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("login/", TokenObtainPairView.as_view()),
    path("token/refresh/", TokenRefreshView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("avatar/", AvatarUploadView.as_view(), name="avatar-upload"),
    path("<int:user_id>/activity/", UserActivityView.as_view(), name="user-activity"),
    path(
        "<str:username>/elo-history/",
        UserEloHistoryView.as_view(),
        name="user-elo-history",
    ),
    # Keep the bare detail route LAST so it doesn't shadow the more specific ones.
    path("<str:username>/", UserDetailView.as_view(), name="user-detail"),
]
