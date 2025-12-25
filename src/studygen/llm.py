import os
from dotenv import load_dotenv

load_dotenv()

def get_api_key() -> str:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY not found. Set it in .env or environment variables.")
    return key

from openai import OpenAI
from .llm import get_api_key

def chat_complete(model: str, user_text: str, temperature: float = 0.3, max_output_tokens: int = 800) -> str:
    client = OpenAI(api_key=get_api_key())
    resp = client.chat.completions.create(
        model=model,
        temperature=temperature,
        max_tokens=max_output_tokens,
        messages=[
            {"role": "system", "content": "You are a precise and helpful assistant."},
            {"role": "user", "content": user_text},
        ],
    )
    return resp.choices[0].message.content.strip()
