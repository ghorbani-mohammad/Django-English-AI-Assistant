import json
import base64
from datetime import datetime

import openai
from openai import OpenAI
from django.conf import settings
from django.utils import timezone
from channels.generic.websocket import WebsocketConsumer

# Import Grammar model
from grammar.models import Grammar

# from log.models import Chat
# from model.models import CachedModel
# from ai.gem import create_cached_model
# from ai.oa import ask_from_azure_oa

# from ai.tunning import get_answer_from_tuned_model


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.uid = self.scope["url_route"]["kwargs"]["uid"]
        self.grammar_id = self.uid
        # Get the grammar from the database and add it to the conversation as context
        self.grammar_context = self.get_grammar_context()
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.conversation = self.grammar_context
        self.cached_model = None
        self.cd_model = None
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
        try:
            # Try to get grammar by ID if grammar_id is a valid integer
            if self.grammar_id.isdigit():
                grammar = Grammar.objects.filter(
                    id=int(self.grammar_id), 
                    deleted_at__isnull=True
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

    def disconnect(self, close_code):
        self.channel_layer.group_discard(self.uid, self.channel_name)

    def send_complete_message(self):
        self.send(json.dumps({"error": False, "message": "completed."}))

    def send_one_part_message(self, message):
        self.send(json.dumps({"error": False, "message": message}))
        self.send_complete_message()

    def get_model_answer(self, model: str, message: str) -> str:
        loaded_model = None
        if model == "gcc":
            pass

    def convert_audio_to_text(self, audio_base64: str) -> str:
        # Split to get the actual base64 part
        header, audio_data = audio_base64.split(",", 1)
        audio_bytes = base64.b64decode(audio_data)
        # Handle the audio bytes (e.g., save to file, send to a service, etc.)
        # Example: save to a file
        file_path = "/app/received_audio.wav"
        with open(file_path, "wb") as f:
            f.write(audio_bytes)

        # Set your OpenAI API key
        openai.api_key = settings.OPENAI_API_KEY

        # Call OpenAI Whisper API to transcribe audio
        with open(file_path, "rb") as audio_file:
            transcript = openai.Audio.transcribe(
                model="whisper-1", file=audio_file  # OpenAI's Whisper model name
            )

        # The response is a dict with 'text' key containing the transcription
        return transcript["text"]

    def thump_up(self, data: dict):
        pass
        # response_id = data["responseId"]
        # print("Received thumb-up data and responseId is " + response_id)
        # chat = Chat.objects.filter(response_id=response_id).first()
        # if not chat:
        #     return
        # chat.thumb_up = chat.thumb_up + 1 if chat.thumb_up else 1
        # chat.save()

    def thumb_down(self, data: dict):
        pass
        # response_id = data["responseId"]
        # print("Received thumb-down data and responseId is " + response_id)
        # chat = Chat.objects.filter(response_id=response_id).first()
        # if not chat:
        # return
        # chat.thumb_down = chat.thumb_down - 1 if chat.thumb_down else -1
        # chat.save()

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

            print(f"Received data: {text_data}")

            # if "command" in data and data["command"] == "thumb-up":
            #     # check if responseId is in data
            #     if "responseId" not in data:
            #         return
            #     self.thump_up(data)
            #     return

            # if "command" in data and data["command"] == "thumb-down":
            #     # check if responseId is in data
            #     if "responseId" not in data:
            #         return
            #     self.thumb_down(data)
            #     return

            # Check if the input is an audio payload
            if "audio" in data:
                print("Received audio data")
                text_data = self.convert_audio_to_text(data["audio"])

            elif "data" in data:
                text_data = data["data"]

            print("User's message: ", text_data)
            self.conversation += f"User: {text_data}\n"

            answer = ""

            # generate random response id
            response_id = datetime.now().strftime("%Y%m%d%H%M%S")

            response_stream = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": self.conversation,
                    }
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
            # Chat.objects.create(
            #     question=text_data, answer=answer, response_id=response_id
            # )
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
