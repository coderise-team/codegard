from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ContestViewSet

router = DefaultRouter()
router.register("", ContestViewSet, basename="contests")

urlpatterns = [
    path("", include(router.urls)),
]
