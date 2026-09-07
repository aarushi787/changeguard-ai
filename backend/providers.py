"""Explicit extension points. Providers must preserve evidence; they cannot release revisions."""
from typing import Protocol
from backend.intelligence import DeterministicProvider

class OCRProvider(Protocol):
    def recognize(self, image: bytes) -> list[dict]:
        """Return text, page/bbox, confidence, and extraction_method for each token."""
        ...

class VisionProvider(Protocol):
    def locate(self, document: bytes) -> list[dict]: ...

class RetrievalProvider(Protocol):
    def retrieve(self, tenant: str, query: str) -> list[dict]:
        """Each result must retain document ID, hash and source location."""
        ...

class ProviderRegistry:
    def __init__(self): self.extraction={'deterministic':DeterministicProvider()}
    def register(self,name,provider):
        if not hasattr(provider,'extract'): raise TypeError('An extraction provider must implement extract(content, suffix).')
        self.extraction[name]=provider
    def get(self,name):
        if name not in self.extraction: raise ValueError('Provider not configured. No silent cloud fallback is permitted.')
        return self.extraction[name]

class MockProvider:
    """Only for explicit tests. Never selected by application configuration."""
    def __init__(self,result): self.result=result
    def extract(self,content,suffix): return self.result
