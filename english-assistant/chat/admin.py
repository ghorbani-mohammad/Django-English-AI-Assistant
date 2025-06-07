from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "sender_type",
        "message_type",
        "user_link",
        "grammar_link",
        "content_preview",
        "created_at",
        "engagement_score",
    ]

    list_filter = [
        "sender_type",
        "message_type",
        "created_at",
        "grammar",
        "user_timezone",
    ]

    search_fields = [
        "content",
        "transcription",
        "user__email",
        "user__first_name",
        "user__last_name",
        "grammar__title",
        "response_id",
        "session_id",
    ]

    readonly_fields = [
        "created_at",
        "updated_at",
        "audio_player",
        "engagement_score",
    ]

    fieldsets = (
        (
            "Message Info",
            {
                "fields": (
                    "user",
                    "grammar",
                    "sender_type",
                    "message_type",
                    "content",
                )
            },
        ),
        (
            "Audio Info",
            {
                "fields": (
                    "audio_file",
                    "audio_player",
                    "audio_duration",
                    "transcription",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Metadata",
            {
                "fields": (
                    "response_id",
                    "session_id",
                    "user_timezone",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Engagement",
            {
                "fields": (
                    "thumb_up",
                    "thumb_down",
                    "engagement_score",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    def user_link(self, obj):
        """Create a link to the user admin page"""
        url = reverse("admin:auth_user_change", args=[obj.user.pk])
        return format_html('<a href="{}">{}</a>', url, obj.user.email)

    user_link.short_description = "User"
    user_link.admin_order_field = "user__email"

    def grammar_link(self, obj):
        """Create a link to the grammar admin page"""
        url = reverse("admin:grammar_grammar_change", args=[obj.grammar.pk])
        return format_html('<a href="{}">{}</a>', url, obj.grammar.title)

    grammar_link.short_description = "Grammar Topic"
    grammar_link.admin_order_field = "grammar__title"

    def content_preview(self, obj):
        """Show a preview of the message content"""
        content = obj.display_content
        if len(content) > 100:
            return content[:100] + "..."
        return content

    content_preview.short_description = "Content Preview"

    def audio_player(self, obj):
        """Display audio player if audio file exists"""
        if obj.audio_file:
            return format_html(
                '<audio controls><source src="{}" type="audio/wav">Your browser does not support the audio element.</audio>',
                obj.audio_file.url,
            )
        return "No audio file"

    audio_player.short_description = "Audio Player"

    def engagement_score(self, obj):
        """Calculate and display engagement score"""
        score = obj.thumb_up - obj.thumb_down
        if score > 0:
            return format_html('<span style="color: green;">+{}</span>', score)
        elif score < 0:
            return format_html('<span style="color: red;">{}</span>', score)
        return score

    engagement_score.short_description = "Engagement"
    engagement_score.admin_order_field = "thumb_up"
