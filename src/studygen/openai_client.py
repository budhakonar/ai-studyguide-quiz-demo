import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Create one client with a sane timeout (prevents indefinite spinners)
client = OpenAI(timeout=60.0)

def require_api_key() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY not found. Set it in .env or environment variables.")

def responses_text(model: str, messages, temperature: float = 0.2, max_output_tokens: int = 900) -> str:
    """
    Standard text generation using the Responses API.
    """
    require_api_key()
    resp = client.responses.create(
        model=model,
        input=messages,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
    )
    # The SDK provides a convenient aggregated helper for text output
    return resp.output_text.strip()
