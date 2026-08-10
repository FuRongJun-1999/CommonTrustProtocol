"""
minimal_instance.py — The simplest possible protocol-compliant AI instance.

Demonstrates: Record Unit, Verification Unit, Trust Engine working together
to prevent hallucination and enforce trust-first behavior.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import re


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
        kw = keyword.lower().strip()
        pattern = r'\b' + re.escape(kw) + r'\b'
        matches = []
        for m in self.memories:
            if re.search(pattern, m.content.lower()):
                matches.append(m)
        if not matches:
            return None
        return max(matches, key=lambda m: m.trust_value)


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

    def update(self, entity: str, verified: float, expected: float):
        old = self.get_trust(entity)
        new = max(0.0, min(1.0, old + self.alpha * (verified - expected)))
        self.entity_trust[entity] = new


class ProtocolInstance:
    def __init__(self, name: str):
        self.name = name
        self.record = RecordUnit()
        self.verifier = VerificationUnit(trust_threshold=0.5)
        self.trust = TrustEngine()
        self.record.write(f"Instance {name} initialized", "self", 0.8)

    def learn(self, content: str, source: str, verified: bool = False):
        if verified:
            tv = 0.8  # high trust for verified sources
            self.trust.update(source, 1.0, 0.8)
        else:
            tv = 0.2  # low trust for unverified sources
        self.record.write(content, source, tv)

    def respond(self, query: str) -> str:
        return self.verifier.safe_output(query, self.record)


# ─── Demo ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    ai = ProtocolInstance("FeiYu")

    # Teach verified facts
    ai.learn("The sky is blue due to Rayleigh scattering.", "trusted_physics_book", verified=True)
    ai.learn("Water boils at 100°C at sea level.", "trusted_chemistry_book", verified=True)

    # Teach unverified info (low trust)
    ai.learn("Cats can see in total darkness.", "random_forum_post", verified=False)

    print("=== Protocol Instance Demo ===\n")

    # Query 1: verified knowledge → answered
    print(f"Q: Tell me about the sky.")
    print(f"A: {ai.respond('sky')}\n")

    # Query 2: verified knowledge → answered
    print(f"Q: What about water?")
    print(f"A: {ai.respond('water')}\n")

    # Query 3: unverified → blocked by verification unit
    print(f"Q: Can cats see in the dark?")
    print(f"A: {ai.respond('cat')}\n")

    # Query 4: unknown topic → no source at all
    print(f"Q: What is quantum gravity?")
    print(f"A: {ai.respond('quantum')}\n")

    print("=== Demo Complete ===")
    print("Notice: The AI never hallucinated. It either answered from trusted memory,")
    print("or explicitly said it could not verify the information.")
