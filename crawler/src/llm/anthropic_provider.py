import os
import json
import anthropic
from .interface import LLMProvider, IssueAnalysis

ANALYSIS_PROMPT = """Analyze this IT support forum post about {application_name} and extract structured information.

Post content:
{content}

Respond with ONLY a JSON object (no markdown, no explanation) with these fields:
- title: A concise title for this issue (max 100 chars)
- summary: A 2-3 sentence summary of the problem and any solutions mentioned
- severity: "critical" (crashes, data loss, security), "major" (significant functionality broken), or "minor" (cosmetic, workarounds exist)
- issue_type: One of "crash", "performance", "install", "security", "compatibility", "ui", "other"
- version_mentioned: The software version mentioned, or null if not specified
- has_workaround: true if a workaround is mentioned, false otherwise

JSON response:"""


class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: str | None = None, model: str = "claude-3-haiku-20240307"):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = model

    def analyze_issue(self, raw_content: str, application_name: str) -> IssueAnalysis:
        prompt = ANALYSIS_PROMPT.format(
            application_name=application_name,
            content=raw_content[:4000]  # Truncate to avoid token limits
        )

        response = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = response.content[0].text.strip()
        data = json.loads(response_text)

        return IssueAnalysis(
            title=data.get("title", "Unknown Issue"),
            summary=data.get("summary", ""),
            severity=data.get("severity", "minor"),
            issue_type=data.get("issue_type"),
            version_mentioned=data.get("version_mentioned"),
            has_workaround=data.get("has_workaround", False)
        )
