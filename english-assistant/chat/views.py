from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Message
from .serializers import (
    MessageSerializer,
    MessageCreateSerializer,
    ChatHistorySerializer,
    MessageEngagementSerializer,
)
from grammar.models import Grammar


class ChatHistoryPagination(PageNumberPagination):
    """Custom pagination for chat history"""

    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 200


class ChatHistoryListView(generics.ListAPIView):
    """List chat history for a specific grammar topic and user"""

    serializer_class = ChatHistorySerializer
    pagination_class = ChatHistoryPagination
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Get messages for specific grammar and user"""
        user = self.request.user
        grammar_id = self.kwargs.get("grammar_id")

        queryset = Message.objects.filter(
            user=user, grammar_id=grammar_id, deleted_at__isnull=True
        ).select_related("user", "grammar")

        # Filter by message type if specified
        message_type = self.request.query_params.get("message_type")
        if message_type in ["text", "audio"]:
            queryset = queryset.filter(message_type=message_type)

        # Filter by sender type if specified
        sender_type = self.request.query_params.get("sender_type")
        if sender_type in ["user", "ai"]:
            queryset = queryset.filter(sender_type=sender_type)

        # Search in content and transcription
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(content__icontains=search) | Q(transcription__icontains=search)
            )

        return queryset.order_by("-created_at")


class AllChatHistoryView(generics.ListAPIView):
    """List all chat history for the authenticated user"""

    serializer_class = MessageSerializer
    pagination_class = ChatHistoryPagination
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Get all messages for the authenticated user"""
        user = self.request.user

        queryset = Message.objects.filter(
            user=user, deleted_at__isnull=True
        ).select_related("user", "grammar")

        # Filter by grammar if specified
        grammar_id = self.request.query_params.get("grammar_id")
        if grammar_id:
            queryset = queryset.filter(grammar_id=grammar_id)

        # Date range filtering
        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")

        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)

        return queryset.order_by("-created_at")


class MessageDetailView(generics.RetrieveAPIView):
    """Retrieve a specific message"""

    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Ensure user can only access their own messages"""
        return Message.objects.filter(
            user=self.request.user, deleted_at__isnull=True
        ).select_related("user", "grammar")


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def update_message_engagement(request, message_id):
    """Update thumbs up/down for a message"""

    message = get_object_or_404(
        Message, id=message_id, user=request.user, deleted_at__isnull=True
    )

    action = request.data.get("action")  # 'thumb_up' or 'thumb_down'

    if action == "thumb_up":
        message.thumb_up += 1
        message.save(update_fields=["thumb_up", "updated_at"])
        return Response(
            {
                "message": "Thumbs up added",
                "thumb_up": message.thumb_up,
                "thumb_down": message.thumb_down,
            }
        )

    elif action == "thumb_down":
        message.thumb_down += 1
        message.save(update_fields=["thumb_down", "updated_at"])
        return Response(
            {
                "message": "Thumbs down added",
                "thumb_up": message.thumb_up,
                "thumb_down": message.thumb_down,
            }
        )

    return Response(
        {"error": "Invalid action. Use 'thumb_up' or 'thumb_down'"},
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def chat_statistics(request):
    """Get chat statistics for the authenticated user"""

    user = request.user

    # Get query parameters for filtering
    grammar_id = request.query_params.get("grammar_id")
    date_from = request.query_params.get("date_from")
    date_to = request.query_params.get("date_to")

    # Base queryset
    queryset = Message.objects.filter(user=user, deleted_at__isnull=True)

    # Apply filters
    if grammar_id:
        queryset = queryset.filter(grammar_id=grammar_id)
    if date_from:
        queryset = queryset.filter(created_at__gte=date_from)
    if date_to:
        queryset = queryset.filter(created_at__lte=date_to)

    # Calculate statistics
    total_messages = queryset.count()
    user_messages = queryset.filter(sender_type="user").count()
    ai_messages = queryset.filter(sender_type="ai").count()
    text_messages = queryset.filter(message_type="text").count()
    audio_messages = queryset.filter(message_type="audio").count()

    # Grammar topics discussed
    grammar_topics = queryset.values("grammar__title", "grammar__id").distinct().count()

    # Engagement metrics
    total_thumbs_up = sum(msg.thumb_up for msg in queryset)
    total_thumbs_down = sum(msg.thumb_down for msg in queryset)

    # Recent activity (last 7 days)
    recent_activity = queryset.filter(
        created_at__gte=timezone.now() - timezone.timedelta(days=7)
    ).count()

    return Response(
        {
            "total_messages": total_messages,
            "user_messages": user_messages,
            "ai_messages": ai_messages,
            "text_messages": text_messages,
            "audio_messages": audio_messages,
            "grammar_topics_discussed": grammar_topics,
            "total_thumbs_up": total_thumbs_up,
            "total_thumbs_down": total_thumbs_down,
            "engagement_score": total_thumbs_up - total_thumbs_down,
            "recent_activity_7_days": recent_activity,
        }
    )


@api_view(["DELETE"])
@permission_classes([permissions.IsAuthenticated])
def delete_chat_history(request, grammar_id):
    """Soft delete chat history for a specific grammar topic"""

    user = request.user

    # Verify grammar exists and user has access
    grammar = get_object_or_404(Grammar, id=grammar_id, deleted_at__isnull=True)

    # Soft delete messages
    messages_updated = Message.objects.filter(
        user=user, grammar=grammar, deleted_at__isnull=True
    ).update(deleted_at=timezone.now())

    return Response(
        {
            "message": f"Chat history deleted for grammar topic: {grammar.title}",
            "messages_deleted": messages_updated,
        }
    )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def export_chat_history(request, grammar_id):
    """Export chat history as JSON for a specific grammar topic"""

    user = request.user
    grammar = get_object_or_404(Grammar, id=grammar_id, deleted_at__isnull=True)

    messages = (
        Message.objects.filter(user=user, grammar=grammar, deleted_at__isnull=True)
        .select_related("user", "grammar")
        .order_by("created_at")
    )

    serializer = MessageSerializer(messages, many=True)

    return Response(
        {
            "grammar_topic": grammar.title,
            "export_date": timezone.now().isoformat(),
            "total_messages": messages.count(),
            "messages": serializer.data,
        }
    )
