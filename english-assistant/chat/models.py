from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from reusable.models import BaseModel
from grammar.models import Grammar


class Message(BaseModel):
    """Model to store chat messages between users and AI assistant"""

    MESSAGE_TYPES = [
        ("text", "Text"),
        ("audio", "Audio"),
    ]

    SENDER_TYPES = [
        ("user", "User"),
        ("ai", "AI Assistant"),
    ]

    # Relations
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="chat_messages",
        help_text="User who initiated the chat session",
    )
    grammar = models.ForeignKey(
        Grammar,
        on_delete=models.CASCADE,
        related_name="chat_messages",
        help_text="Grammar topic being discussed",
    )

    # Message content
    content = models.TextField(help_text="Text content of the message")
    message_type = models.CharField(
        max_length=10,
        choices=MESSAGE_TYPES,
        default="text",
        help_text="Type of message (text or audio)",
    )
    sender_type = models.CharField(
        max_length=10,
        choices=SENDER_TYPES,
        help_text="Who sent the message (user or AI)",
    )

    # Audio specific fields
    audio_file = models.FileField(
        upload_to="chat_audio/%Y/%m/%d/",
        null=True,
        blank=True,
        help_text="Audio file for voice messages",
    )
    audio_duration = models.FloatField(
        null=True, blank=True, help_text="Duration of audio message in seconds"
    )
    transcription = models.TextField(
        null=True, blank=True, help_text="Transcription of audio message"
    )

    # Metadata
    response_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Unique identifier for AI responses",
    )
    session_id = models.CharField(
        max_length=100, null=True, blank=True, help_text="WebSocket session identifier"
    )
    user_timezone = models.CharField(
        max_length=50, default="UTC", help_text="User's timezone when message was sent"
    )

    # Engagement metrics
    thumb_up = models.IntegerField(default=0, help_text="Number of thumbs up received")
    thumb_down = models.IntegerField(
        default=0, help_text="Number of thumbs down received"
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "grammar", "-created_at"]),
            models.Index(fields=["response_id"]),
            models.Index(fields=["session_id"]),
            models.Index(fields=["sender_type", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.sender_type.title()} message in {self.grammar.title} - {self.created_at}"

    @property
    def is_user_message(self):
        """Check if message is from user"""
        return self.sender_type == "user"

    @property
    def is_ai_message(self):
        """Check if message is from AI"""
        return self.sender_type == "ai"

    @property
    def is_audio_message(self):
        """Check if message is audio type"""
        return self.message_type == "audio"

    @property
    def display_content(self):
        """Get display content (transcription for audio, content for text)"""
        if self.is_audio_message and self.transcription:
            return self.transcription
        return self.content

    @classmethod
    def create_user_message(cls, user, grammar, content, message_type="text", **kwargs):
        """Create a user message"""
        return cls.objects.create(
            user=user,
            grammar=grammar,
            content=content,
            message_type=message_type,
            sender_type="user",
            **kwargs,
        )

    @classmethod
    def create_ai_message(cls, user, grammar, content, response_id=None, **kwargs):
        """Create an AI message"""
        return cls.objects.create(
            user=user,
            grammar=grammar,
            content=content,
            message_type="text",
            sender_type="ai",
            response_id=response_id,
            **kwargs,
        )
