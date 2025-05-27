from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GrammarViewSet

router = DefaultRouter()
router.register(r"grammar", GrammarViewSet, basename="grammar")

urlpatterns = [
    path("", include(router.urls)),
]
