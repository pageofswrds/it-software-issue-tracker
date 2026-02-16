from dataclasses import dataclass


@dataclass
class WebSearchResult:
    url: str
    title: str
    snippet: str
    source: str


@dataclass
class FetchedPage:
    url: str
    title: str
    content: str
    source: str
