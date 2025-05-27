from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExpressionViewSet

router = DefaultRouter()
router.register(r"expression", ExpressionViewSet, basename="expression")

urlpatterns = [
    path("", include(router.urls)),
]
