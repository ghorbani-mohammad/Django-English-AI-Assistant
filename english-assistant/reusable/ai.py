from typing import Optional

import openai
from openai import OpenAI
from django.conf import settings


def query_openai(query: str, model: str = "gpt-4o-mini") -> Optional[str]:
    client = OpenAI(
        # This is the default and can be omitted
        api_key=settings.OPENAI_API_KEY,
        organization=settings.OPENAI_ORG_ID,
    )
    result = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": query,
            }
        ],
        model=model,
    )
    if result.choices[0].finish_reason != "stop":
        return None
    return result.choices[0].message.content


def query_deepseek(query: str) -> str:
    # Initialize the OpenAI client with DeepSeek's base URL
    openai.api_key = settings.DEEPSEEK_API_KEY
    openai.api_base = settings.DEEPSEEK_BASE_URL

    # Define the conversation messages
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": query},
    ]

    # Make the API call to DeepSeek's chat completions endpoint
    response = openai.ChatCompletion.create(
        model="deepseek-chat", messages=messages, stream=False
    )

    # Print the assistant's reply
    print(response["choices"][0]["message"]["content"])


def get_answer(query: str) -> str:
    client = OpenAI(api_key=settings.METIS_API_KEY, base_url=settings.METIS_BASE_URL)
    response = client.chat.completions.create(
        model="gpt-4o", messages=[{"role": "user", "content": query}], max_tokens=100
    )

    return response.choices[0].message.content


def get_grammar_introduction(grammar_info: str) -> str:
    question = (
        "Hey, can you write a grammar introduction for me? Please at most, 150 words."
    )
    query = f"{question}\n\n{grammar_info}"
    return query_openai(query)
