from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class IssueAnalysis:
    title: str
    summary: str
    severity: str  # 'critical', 'major', 'minor'
    issue_type: str | None = None  # 'crash', 'performance', 'install', 'security', etc.
    version_mentioned: str | None = None
    has_workaround: bool = False


class LLMProvider(ABC):
    @abstractmethod
    def analyze_issue(self, raw_content: str, application_name: str) -> IssueAnalysis:
        """Analyze raw content and extract structured issue information."""
        pass
