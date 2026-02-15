from .interface import LLMProvider, IssueAnalysis
from .anthropic_provider import AnthropicProvider


def get_llm_provider(provider_name: str = "anthropic") -> LLMProvider:
    if provider_name == "anthropic":
        return AnthropicProvider()
    else:
        raise ValueError(f"Unknown LLM provider: {provider_name}")


__all__ = ['LLMProvider', 'IssueAnalysis', 'get_llm_provider', 'AnthropicProvider']
