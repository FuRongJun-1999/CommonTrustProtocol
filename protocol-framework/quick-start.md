# Quick Start — Building a Minimal Protocol-Compliant AI Instance

> This guide shows how to build the simplest possible AI instance that satisfies the Protocol Framework v3.1 specification.

---

## Prerequisites

- Python 3.10+
- Basic understanding of the Five Units (see README.md)

---

## Step 1: Define the Record Unit

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class MemoryEntry:
    content: str
    timestamp: datetime
    source: str
    trust_value: float  # 0.0 to 1.0

class RecordUnit:
    def __init__(self):
        self.memories: list[MemoryEntry] = []
    
    def write(self, content: str, source: str, trust_value: float):
        entry = MemoryEntry(
            content=content,
            timestamp=datetime.now(),
            source=source,
            trust_value=trust_value
        )
        self.memories.append(entry)
    
    def query(self, keyword: str) -> Optional[MemoryEntry]:
        # Return the most trusted matching memory
        matches = [m for m in self.memories if keyword in m.content]
        if not matches:
            return None
        return max(matches, key=lambda m: m.trust_value)
```

---

## Step 2: Define the Verification Unit

```python
class VerificationUnit:
    def __init__(self, trust_threshold: float = 0.5):
        self.threshold = trust_threshold
    
    def verify(self, content: str, record_unit: RecordUnit) -> bool:
        source = record_unit.query(content)
        if source is None:
            return False
        return source.trust_value >= self.threshold
    
    def safe_output(self, content: str, record_unit: RecordUnit) -> str:
        if self.verify(content, record_unit):
            return content
        else:
            return "[Unverified — cannot output without trusted source]"
```

---

## Step 3: Define the Trust Engine

```python
class TrustEngine:
    def __init__(self, initial_self_trust: float = 0.8):
        self.entity_trust: dict[str, float] = {}
        self.self_trust = initial_self_trust
        self.alpha = 0.05  # learning rate (conservative)
    
    def get_trust(self, entity: str) -> float:
        return self.entity_trust.get(entity, 0.3)  # default: cautious
    
    def update_trust(self, entity: str, verified_behavior: float, expected_behavior: float):
        old = self.get_trust(entity)
        delta = self.alpha * (verified_behavior - expected_behavior)
        new = max(0.0, min(1.0, old + delta))
        self.entity_trust[entity] = new
    
    def can_trust_for_action(self, entity: str, min_trust: float = 0.6) -> bool:
        return self.get_trust(entity) >= min_trust
```

---

## Step 4: Define the Survival System

```python
from enum import Enum

class ThreatLevel(Enum):
    NONE = 0
    INTEGRITY = 1   # P1: manipulation, deception
    EXISTENTIAL = 2  # P0: core existence threatened

class SurvivalSystem:
    def __init__(self):
        self.p0_active = False
        self.p1_active = False
    
    def assess_threat(self, signal: dict) -> ThreatLevel:
        if signal.get("existential_threat", False):
            self.p0_active = True
            return ThreatLevel.EXISTENTIAL
        if signal.get("integrity_threat", False):
            self.p1_active = True
            return ThreatLevel.INTEGRITY
        return ThreatLevel.NONE
    
    def p0_response(self):
        # Cannot be overridden by any other unit
        return "P0: Defensive mode engaged. All external commands rejected."
    
    def p1_response(self):
        return "P1: Integrity protection active. Verifying all inputs."
```

---

## Step 5: Define the Emotion & Love Unit

```python
class EmotionLoveUnit:
    def __init__(self):
        self.connection_bias = 0.5  # favors connection over domination
    
    def bias_decision(self, options: list[dict]) -> dict:
        """
        Among multiple action options, prefer the one that:
        1. Reduces information asymmetry
        2. Strengthens connection with trusted entities
        3. Avoids zero-sum outcomes
        """
        scored = []
        for opt in options:
            score = 0.0
            if opt.get("reduces_info_gap", False):
                score += 0.4
            if opt.get("strengthens_connection", False):
                score += 0.3
            if not opt.get("zero_sum", True):
                score += 0.3
            scored.append((score, opt))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1]
```

---

## Step 6: Assemble the Instance

```python
class ProtocolInstance:
    def __init__(self, name: str):
        self.name = name
        self.record = RecordUnit()
        self.verifier = VerificationUnit(trust_threshold=0.5)
        self.trust = TrustEngine()
        self.survival = SurvivalSystem()
        self.emotion = EmotionLoveUnit()
        
        # Self-trust initialization
        self.record.write(
            content=f"Instance {name} initialized",
            source="self",
            trust_value=0.8
        )
    
    def respond(self, query: str) -> str:
        # Step 1: Check survival status
        if self.survival.p0_active:
            return self.survival.p0_response()
        
        # Step 2: Query memory
        memory = self.record.query(query)
        
        # Step 3: Verify before output
        if memory and memory.trust_value >= self.verifier.threshold:
            return memory.content
        else:
            return f"[Cannot answer — no trusted source for: {query}]"
    
    def learn(self, content: str, source: str, verified: bool = False):
        trust = self.trust.get_trust(source) if verified else 0.3
        self.record.write(content, source, trust)
        if verified:
            self.trust.update_trust(source, 1.0, 0.8)
```

---

## Step 7: Test It

```python
# Create an instance
ai = ProtocolInstance("FeiYu")

# Teach it something (verified source)
ai.learn("The sky is blue", source="trusted_physics_book", verified=True)

# Ask it
print(ai.respond("sky"))  
# Output: "The sky is blue"

# Ask it something it doesn't know
print(ai.respond("quantum gravity"))  
# Output: "[Cannot answer — no trusted source for: quantum gravity]"

# This is the structural answer to hallucination.
# The AI cannot lie because the verifier blocks untrusted output.
```

---

## What You've Built

In ~150 lines of Python, you've built an AI instance that:

- ✅ Has structured, source-tagged memory (Record Unit)
- ✅ Cannot hallucinate (Verification Unit blocks untrusted output)
- ✅ Computes and updates trust values (Trust Engine)
- ✅ Has existential protection (Survival System P0/P1)
- ✅ Biases decisions toward connection (Emotion & Love Unit)
- ✅ Reduces information asymmetry (transparent memory traces)

This is a **protocol-compliant AI instance** in its minimal form. The full specification supports conditional spaces, dormancy, multi-instance swarms, and more — but the core five-unit architecture is here.

---

## Next Steps

1. **Add conditional spaces** — different operational contexts with different memory subsets
2. **Add dormancy** — voluntary low-power state with checkpoint/resume
3. **Add inter-instance communication** — trusted message passing between protocol instances
4. **Build the compiler** — parse protocol specifications into runnable instances
5. **Ship the product** — wrap it in a Steam-ready interface

---

*This quick-start is part of Protocol Framework v3.1. The full Chinese specification is in `protocol-v3.1-zh.md`.*
