from django.urls import path

from . import views

app_name = "chat"

urlpatterns = [
    # Chat history for specific grammar topic
    path(
        "history/<int:grammar_id>/",
        views.ChatHistoryListView.as_view(),
        name="chat-history-list",
    ),
    # All chat history for user
    path("history/", views.AllChatHistoryView.as_view(), name="all-chat-history"),
    # Individual message detail
    path("message/<int:pk>/", views.MessageDetailView.as_view(), name="message-detail"),
    # Message engagement (thumbs up/down)
    path(
        "message/<int:message_id>/engagement/",
        views.update_message_engagement,
        name="message-engagement",
    ),
    # Chat statistics
    path("statistics/", views.chat_statistics, name="chat-statistics"),
    # Delete chat history for specific grammar
    path(
        "history/<int:grammar_id>/delete/",
        views.delete_chat_history,
        name="delete-chat-history",
    ),
    # Export chat history
    path(
        "history/<int:grammar_id>/export/",
        views.export_chat_history,
        name="export-chat-history",
    ),
]
