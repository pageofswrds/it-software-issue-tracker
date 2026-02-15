import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

EMBEDDING_DIMENSION = 1536
EMBEDDING_MODEL = "text-embedding-3-small"

_client = None

def _get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set")
        _client = OpenAI(api_key=api_key)
    return _client

def get_embedding(text: str) -> list[float]:
    """Generate embedding for the given text using OpenAI's embedding model."""
    client = _get_client()

    # Truncate text if too long (max ~8000 tokens for this model)
    text = text[:30000]

    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )

    return response.data[0].embedding
