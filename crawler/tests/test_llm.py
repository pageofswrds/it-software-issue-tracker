import pytest
import os
from src.llm import get_llm_provider
from src.llm.interface import LLMProvider, IssueAnalysis

def test_llm_provider_interface():
    # Test that interface defines required methods
    assert hasattr(LLMProvider, 'analyze_issue')

def test_issue_analysis_structure():
    analysis = IssueAnalysis(
        title="Test Issue",
        summary="This is a test",
        severity="critical",
        issue_type="crash",
        version_mentioned="1.0.0",
        has_workaround=False
    )
    assert analysis.title == "Test Issue"
    assert analysis.severity == "critical"

def test_get_llm_provider_returns_anthropic():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        pytest.skip("ANTHROPIC_API_KEY not set")
    provider = get_llm_provider("anthropic")
    assert provider is not None
