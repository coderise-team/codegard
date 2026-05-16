from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProblemViewSet

router = DefaultRouter()
router.register("", ProblemViewSet, basename="problems")

urlpatterns = [
    path("", include(router.urls)),
]
