from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    AvatarUploadView,
    LoginView,
    LogoutView,
    MeView,
    RegisterView,
    UserActivityView,
    UserDetailView,
    UserEloHistoryView,
)

app_name = "users"

urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("login/", LoginView.as_view()),
    path("token/refresh/", TokenRefreshView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("avatar/", AvatarUploadView.as_view(), name="avatar-upload"),
    path("me/", MeView.as_view()),
    path("<int:user_id>/activity/", UserActivityView.as_view(), name="user-activity"),
    path(
        "<str:username>/elo-history/",
        UserEloHistoryView.as_view(),
        name="user-elo-history",
    ),
    # Keep the bare detail route LAST so it doesn't shadow the more specific ones.
    path("<str:username>/", UserDetailView.as_view(), name="user-detail"),
]
