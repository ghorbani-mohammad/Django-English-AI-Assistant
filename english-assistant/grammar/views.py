from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from . import models, serializers


class GrammarViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A readonly viewset for viewing Grammar instances.
    Provides list and retrieve actions only.
    """
    queryset = models.Grammar.objects.filter(deleted_at__isnull=True)
    serializer_class = serializers.GrammarSerializer
    permission_classes = [AllowAny]
