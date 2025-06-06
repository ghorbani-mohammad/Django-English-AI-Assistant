from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination


from . import models, serializers


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class ExpressionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A readonly viewset for viewing Expression instances.
    Provides list and retrieve actions only.
    """

    queryset = models.Expression.objects.filter(deleted_at__isnull=True).order_by("-id")
    serializer_class = serializers.ExpressionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
