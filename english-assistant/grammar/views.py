from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination

from . import models, serializers


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class GrammarViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A readonly viewset for viewing Grammar instances.
    Provides list and retrieve actions only.
    """
    queryset = models.Grammar.objects.filter(deleted_at__isnull=True)
    serializer_class = serializers.GrammarSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination