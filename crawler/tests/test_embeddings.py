import pytest
from src.embeddings import get_embedding, EMBEDDING_DIMENSION

def test_embedding_dimension_constant():
    assert EMBEDDING_DIMENSION == 1536

def test_get_embedding_returns_correct_dimension():
    # This test requires OPENAI_API_KEY
    # Skip if not available
    import os
    if not os.environ.get("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set")

    embedding = get_embedding("This is a test sentence")
    assert len(embedding) == EMBEDDING_DIMENSION
    assert all(isinstance(x, float) for x in embedding)
