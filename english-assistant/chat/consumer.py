import json
import base64
import os
from datetime import datetime

import openai
from openai import OpenAI
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser
from django.core.files.base import ContentFile
from channels.generic.websocket import WebsocketConsumer

# Import Grammar model
from grammar.models import Grammar
from .models import Message

# from log.models import Chat
# from model.models import CachedModel
# from ai.gem import create_cached_model
# from ai.oa import ask_from_azure_oa

# from ai.tunning import get_answer_from_tuned_model


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        # Check if user is authenticated
        user = self.scope.get("user")
        if not user or isinstance(user, AnonymousUser):
            self.close(code=4001)  # Custom close code for unauthorized
            return

        self.uid = self.scope["url_route"]["kwargs"]["uid"]
        self.grammar_id = self.uid
        self.user = user  # Store authenticated user

        # Get the grammar from the database and add it to the conversation as context
        self.grammar_context = self.get_grammar_context()
        self.grammar_obj = self.get_grammar_object()
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.conversation = ""
        self.cached_model = None
        self.cd_model = None

        # Generate session ID for this WebSocket connection
        self.session_id = f"{self.user.id}_{self.grammar_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        if self.uid == "1":
            # ai bot
            print("socket from flutter project, let's load the cached model")
        self.channel_layer.group_add(self.uid, self.channel_name)
        self.accept()
        # self.send_one_part_message(
        #     "Hi, I'm your English AI assistant. How can I help you today?"
        # )

    def get_grammar_context(self) -> str:
        """
        Retrieve grammar from database and format it as context for the conversation.
        """
        if not self.grammar_id:
            raise ValueError("Grammar ID is required")
        if not self.grammar_id.isdigit():
            raise ValueError("Grammar ID must be a valid integer")
        try:
            grammar = Grammar.objects.filter(
                id=int(self.grammar_id), deleted_at__isnull=True
            ).first()

            if grammar:
                context = f"""You are an English AI assistant specializing in the following grammar topic:

Grammar Topic: {grammar.title}
Description: {grammar.description}

Please help users with questions related to this grammar topic. Provide clear explanations, examples, and corrections when needed. Always be encouraging and supportive in your responses.

Conversation History:
"""
                return context

            # If no specific grammar found or grammar_id is not a number, provide general context
            return """You are an English AI assistant. Help users with grammar, vocabulary, pronunciation, and general English language questions. Provide clear explanations, examples, and corrections when needed. Always be encouraging and supportive in your responses.

Conversation History:
"""
        except Exception as e:
            print(f"Error retrieving grammar context: {e}")
            return """You are an English AI assistant. Help users with grammar, vocabulary, pronunciation, and general English language questions. Provide clear explanations, examples, and corrections when needed. Always be encouraging and supportive in your responses.

Conversation History:
"""

    def get_grammar_object(self):
        """Get the Grammar object for this conversation"""
        if not self.grammar_id or not self.grammar_id.isdigit():
            return None
        try:
            return Grammar.objects.filter(
                id=int(self.grammar_id), deleted_at__isnull=True
            ).first()
        except Exception as e:
            print(f"Error retrieving grammar object: {e}")
            return None

    def disconnect(self, close_code):
        if hasattr(self, "uid") and hasattr(self, "channel_name"):
            self.channel_layer.group_discard(self.uid, self.channel_name)

        if close_code == 4001:
            print(f"WebSocket connection closed: Unauthorized access attempt")

    def send_complete_message(self):
        self.send(json.dumps({"error": False, "message": "completed."}))

    def send_one_part_message(self, message):
        self.send(json.dumps({"error": False, "message": message}))
        self.send_complete_message()

    def get_model_answer(self, model: str, message: str) -> str:
        loaded_model = None
        if model == "gcc":
            pass

    def convert_audio_to_text(self, audio_base64: str) -> tuple:
        """Convert audio to text and return transcription with audio file"""
        # Split to get the actual base64 part
        header, audio_data = audio_base64.split(",", 1)
        audio_bytes = base64.b64decode(audio_data)

        # Generate unique filename for this audio
        audio_filename = (
            f"audio_{self.user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        )

        # Save to temporary file for Whisper processing
        temp_file_path = f"/tmp/{audio_filename}"
        with open(temp_file_path, "wb") as f:
            f.write(audio_bytes)

        # Call OpenAI Whisper API to transcribe audio
        with open(temp_file_path, "rb") as audio_file:
            transcript = self.client.audio.transcriptions.create(
                model="whisper-1", file=audio_file
            )

        # Create Django file object for saving to model
        audio_file_obj = ContentFile(audio_bytes, name=audio_filename)

        # Clean up temporary file
        try:
            os.remove(temp_file_path)
        except OSError:
            pass

        return transcript.text, audio_file_obj

    def save_user_message(
        self, content, message_type="text", audio_file=None, transcription=None
    ):
        """Save user message to database"""
        if not self.grammar_obj:
            print("Warning: No grammar object found, skipping message save")
            return None

        try:
            message = Message.create_user_message(
                user=self.user,
                grammar=self.grammar_obj,
                content=content,
                message_type=message_type,
                session_id=self.session_id,
                user_timezone=str(timezone.get_current_timezone()),
                audio_file=audio_file,
                transcription=transcription,
            )
            print(f"Saved user message: {message.id}")
            return message
        except Exception as e:
            print(f"Error saving user message: {e}")
            return None

    def save_ai_message(self, content, response_id=None):
        """Save AI message to database"""
        if not self.grammar_obj:
            print("Warning: No grammar object found, skipping message save")
            return None

        try:
            message = Message.create_ai_message(
                user=self.user,
                grammar=self.grammar_obj,
                content=content,
                response_id=response_id,
                session_id=self.session_id,
                user_timezone=str(timezone.get_current_timezone()),
            )
            print(f"Saved AI message: {message.id}")
            return message
        except Exception as e:
            print(f"Error saving AI message: {e}")
            return None

    def thump_up(self, data: dict):
        """Handle thumbs up for a message"""
        response_id = data.get("responseId")
        if not response_id:
            print("No responseId provided for thumb up")
            return

        try:
            message = Message.objects.filter(
                response_id=response_id, user=self.user, deleted_at__isnull=True
            ).first()

            if message:
                message.thumb_up += 1
                message.save(update_fields=["thumb_up", "updated_at"])
                print(f"Thumb up added to message {message.id}")
            else:
                print(f"Message with response_id {response_id} not found")
        except Exception as e:
            print(f"Error processing thumb up: {e}")

    def thumb_down(self, data: dict):
        """Handle thumbs down for a message"""
        response_id = data.get("responseId")
        if not response_id:
            print("No responseId provided for thumb down")
            return

        try:
            message = Message.objects.filter(
                response_id=response_id, user=self.user, deleted_at__isnull=True
            ).first()

            if message:
                message.thumb_down += 1
                message.save(update_fields=["thumb_down", "updated_at"])
                print(f"Thumb down added to message {message.id}")
            else:
                print(f"Message with response_id {response_id} not found")
        except Exception as e:
            print(f"Error processing thumb down: {e}")

    def receive(self, text_data=None, bytes_data=None):
        if text_data:
            # Parse the text_data to check if it's JSON
            try:
                data = json.loads(text_data)
            except json.JSONDecodeError:
                print(f"Received non-JSON text data. Received: {text_data}")
                return

            if "command" in data and data["command"] == "ping":
                print(f"Just pinging")
                return

            if "command" in data and data["command"] == "thumb-up":
                # check if responseId is in data
                if "responseId" not in data:
                    return
                self.thump_up(data)
                return

            if "command" in data and data["command"] == "thumb-down":
                # check if responseId is in data
                if "responseId" not in data:
                    return
                self.thumb_down(data)
                return

            # Check if the input is an audio payload
            if "audio" in data:
                print("Received audio data")
                transcription, audio_file = self.convert_audio_to_text(data["audio"])

                # Save user audio message
                self.save_user_message(
                    content=transcription,
                    message_type="audio",
                    audio_file=audio_file,
                    transcription=transcription,
                )

                self.send(json.dumps({"error": False, "audio_text": transcription}))
                self.send_complete_message()

                # Use transcription as the text_data for AI processing
                text_data = transcription

            elif "data" in data:
                text_data = data["data"]
                print(f"Received data: {text_data}")

                # Save user text message
                self.save_user_message(content=text_data, message_type="text")

            print(f"User {self.user.email} message: {text_data}")
            self.conversation += f"User ({self.user.email}): {text_data}\n"

            answer = ""

            # generate random response id
            response_id = datetime.now().strftime("%Y%m%d%H%M%S")

            response_stream = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are an English AI assistant specializing in the following grammar topic: {self.grammar_context}",
                    },
                    # follow the max tokens limit
                    {
                        "role": "system",
                        "content": f"You can only answer in 300 tokens",
                    },
                    {
                        "role": "user",
                        "content": self.conversation,
                    },
                ],
                temperature=0,
                max_tokens=300,  # Adjust based on desired response length
                stream=True,
            )

            for chunk in response_stream:
                for choice in chunk.choices:
                    part = choice.delta.content
                    if not part:
                        continue
                    answer += part
                    self.send(
                        json.dumps({"error": False, "message": part, "id": response_id})
                    )
            self.send_complete_message()

            # Save AI response message
            self.save_ai_message(content=answer, response_id=response_id)

            self.conversation += f"AI assistant Answer: {answer}\n"

    def stream_audio(self, text_data):
        self.time_of_starting_audio = datetime.now()
        response = self.client.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice="alloy",
            input=text_data,
        )
        self.first_byte_of_audio = datetime.now()
        for chunk in response.iter_bytes(chunk_size=1024):
            self.send(chunk)  # Sending audio chunks directly
        self.time_of_ending_audio = datetime.now()
