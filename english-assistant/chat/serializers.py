from rest_framework import serializers
from django.contrib.auth.models import User

from .models import Message
from grammar.serializers import GrammarSerializer


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model"""

    user_email = serializers.CharField(source="user.email", read_only=True)
    user_name = serializers.SerializerMethodField()
    grammar_title = serializers.CharField(source="grammar.title", read_only=True)
    display_content = serializers.CharField(read_only=True)
    is_user_message = serializers.BooleanField(read_only=True)
    is_ai_message = serializers.BooleanField(read_only=True)
    is_audio_message = serializers.BooleanField(read_only=True)
    engagement_score = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            "id",
            "user",
            "user_email",
            "user_name",
            "grammar",
            "grammar_title",
            "content",
            "display_content",
            "message_type",
            "sender_type",
            "audio_file",
            "audio_duration",
            "transcription",
            "response_id",
            "session_id",
            "user_timezone",
            "thumb_up",
            "thumb_down",
            "engagement_score",
            "is_user_message",
            "is_ai_message",
            "is_audio_message",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def get_user_name(self, obj):
        """Get user's full name or email"""
        if obj.user.first_name or obj.user.last_name:
            return f"{obj.user.first_name} {obj.user.last_name}".strip()
        return obj.user.email

    def get_engagement_score(self, obj):
        """Calculate engagement score"""
        return obj.thumb_up - obj.thumb_down


class MessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating messages"""

    class Meta:
        model = Message
        fields = [
            "user",
            "grammar",
            "content",
            "message_type",
            "sender_type",
            "audio_file",
            "audio_duration",
            "transcription",
            "response_id",
            "session_id",
            "user_timezone",
        ]

    def validate(self, data):
        """Validate message data"""
        # Ensure audio messages have either audio_file or transcription
        if data.get("message_type") == "audio":
            if not data.get("audio_file") and not data.get("transcription"):
                raise serializers.ValidationError(
                    "Audio messages must have either an audio file or transcription"
                )

        return data


class ChatHistorySerializer(serializers.ModelSerializer):
    """Simplified serializer for chat history display"""

    user_name = serializers.SerializerMethodField()
    display_content = serializers.CharField(read_only=True)
    formatted_date = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            "id",
            "user_name",
            "display_content",
            "message_type",
            "sender_type",
            "audio_file",
            "audio_duration",
            "formatted_date",
            "created_at",
        ]

    def get_user_name(self, obj):
        """Get user's display name"""
        if obj.sender_type == "ai":
            return "AI Assistant"
        if obj.user.first_name or obj.user.last_name:
            return f"{obj.user.first_name} {obj.user.last_name}".strip()
        return obj.user.email.split("@")[0]

    def get_formatted_date(self, obj):
        """Get formatted date for display"""
        return obj.created_at.strftime("%Y-%m-%d %H:%M:%S")


class MessageEngagementSerializer(serializers.ModelSerializer):
    """Serializer for updating message engagement (thumbs up/down)"""

    class Meta:
        model = Message
        fields = ["thumb_up", "thumb_down"]

    def validate(self, data):
        """Ensure thumb values are non-negative"""
        if data.get("thumb_up", 0) < 0:
            raise serializers.ValidationError("Thumb up count cannot be negative")
        if data.get("thumb_down", 0) < 0:
            raise serializers.ValidationError("Thumb down count cannot be negative")
        return data
