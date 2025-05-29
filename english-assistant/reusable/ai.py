import os
from typing import Optional

from openai import OpenAI


def query_openai(query: str, model: str = "gpt-4o-mini") -> Optional[str]:
    client = OpenAI(
        # This is the default and can be omitted
        api_key=os.environ.get("OPENAI_API_KEY"),
        organization=os.environ.get("OPENAI_ORG_ID"),
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


def get_grammar_introduction(grammar_info: str) -> str:
    question = "Hey, can you write a grammar introduction for me? Please at most, 150 words."
    query = f"{question}\n\n{grammar_info}"
    return query_openai(query)
