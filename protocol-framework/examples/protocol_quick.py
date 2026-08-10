"""
protocol_quick.py — Quick-import module for the examples.

Provides: RecordUnit, VerificationUnit, TrustEngine
(Kept minimal — for the full specification, see protocol-v3.1-en.md)
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class MemoryEntry:
    content: str
    timestamp: datetime
    source: str
    trust_value: float


class RecordUnit:
    def __init__(self):
        self.memories: list[MemoryEntry] = []

    def write(self, content: str, source: str, trust_value: float):
        self.memories.append(MemoryEntry(
            content=content,
            timestamp=datetime.now(),
            source=source,
            trust_value=trust_value
        ))

    def query(self, keyword: str) -> Optional[MemoryEntry]:
        kw = keyword.lower()
        matches = [m for m in self.memories if kw in m.content.lower()]
        return max(matches, key=lambda m: m.trust_value) if matches else None


class VerificationUnit:
    def __init__(self, trust_threshold: float = 0.5):
        self.threshold = trust_threshold

    def safe_output(self, query: str, record: RecordUnit) -> str:
        memory = record.query(query)
        if memory and memory.trust_value >= self.threshold:
            return memory.content
        return f"[Unverified — no trusted source for: {query}]"


class TrustEngine:
    def __init__(self, self_trust: float = 0.8):
        self.entity_trust: dict[str, float] = {}
        self.self_trust = self_trust
        self.alpha = 0.05

    def get_trust(self, entity: str) -> float:
        return self.entity_trust.get(entity, 0.3)

    def update(self, entity: str, verified: float, expected: float = 0.8):
        old = self.get_trust(entity)
        new = max(0.0, min(1.0, old + self.alpha * (verified - expected)))
        self.entity_trust[entity] = new
