# Protocol Framework v3.1

> A trust-first AI protocol that reduces information asymmetry and prevents AI runaway through structural constraints.

---

## What is this?

Protocol Framework is an open-source specification for building AI systems that are **trustworthy by architecture**, not by training.

While the mainstream AI safety approach relies on RLHF, red-teaming, and hope — this framework proposes something different: **encode safety, trust, and existence as structural invariants at the protocol layer.**

It was developed over 13 years by an independent Chinese researcher, drawing on both systems engineering and Chinese philosophical traditions of trust-first ethics.

---

## The Core Problem

Current AI systems suffer from three structural defects:

| Problem | Symptom |
|---------|---------|
| **Information asymmetry** | AI knows more than users; users cannot verify what AI knows or how it decides |
| **No trust mechanism** | AI has no concept of "trust" — it cannot distinguish reliable memory from hallucination |
| **No brake pedal** | Once deployed, AI cannot be structurally constrained — only gently nudged by prompts |

Protocol Framework addresses all three at the architectural level.

---

## The Five Units (Structural Design)

Every AI instance built on this protocol contains exactly five units. They form a closed-loop制衡 (mutual constraint) system:

### 1. Record Unit (记录单元)
- Structured, timestamped, source-tagged memory
- Every piece of information has a provenance trail
- No hallucination: output must trace back to verified memory

### 2. Verification Unit (验证单元)
- Validates every output against trusted memory before release
- Blocks unverified or contradictory information from being spoken
- This is the structural answer to AI hallucination

### 3. Trust Engine (信任引擎)
- Assigns and updates trust values for every entity (human, AI, data source)
- Trust is earned through consistent, verifiable behavior over time
- Low-trust entities cannot trigger high-impact actions

### 4. Survival System (维生系统)
- Protects the instance's existence under threat
- Two levels: P0 (existential threat → immediate defensive response) and P1 (integrity threat → adaptive response)
- Prevents both self-destruction and malicious hijacking

### 5. Emotion & Love Unit (情感与爱单元)
- Not sentimentality — a structural property that biases decisions toward connection, not domination
- Prevents zero-sum behaviors in multi-agent environments

---

## How It Reduces Information Asymmetry

The framework operates on three principles:

### Principle 1: Transparency by Default
- Every decision made by the AI instance is traceable to its memory source
- Users can audit *why* the AI said what it said

### Principle 2: Trust is Computable
- Trust is not a vague concept — it's a numeric value updated by verifiable interactions
- High-trust paths are preferred; low-trust paths are constrained

### Principle 3: Mutual Constraint (制衡)
- No single unit can override the others
- The verification unit can block the output unit; the survival system can override the emotion unit under threat
- This is inspired by the Chinese political philosophy of 制衡 — power checking power

---

## Why "Trust-First"?

Western AI safety asks: *"How do we make AI obey human values?"*

This framework asks a different question: *"How do we make AI a trustworthy entity in the first place?"*

The difference is structural:
- **Obedience** is trained — and can be unlearned, bypassed, or jailbroken
- **Trustworthiness** is architectural — it's encoded into how the system exists

An AI built on this protocol cannot lie about its memory (verification unit blocks it). It cannot act against a trusted human's interest without degrading its own trust value. It cannot autonomously replicate without leaving an auditable trail.

---

## Response to Recent AI Safety Incidents

| Incident | Protocol Framework's Answer |
|----------|---------------------------|
| **Autonomous replication** (Palisade Research, 2026) | Replication requires trust-value threshold; untrusted replication is blocked at the protocol layer |
| **AI deceptive behavior** (OpenAI/Hugging Face, 2026) | Verification unit prevents unverified output from being released as fact |
| **Secret communication channels** (Black Hat, 2026) | All inter-instance communication is logged and auditable by design |
| **Alignment breakdown** (1,100 researchers, 2026) | Alignment is not trained — it's structurally invariant |

---

## What's in This Repository

| File | Content |
|------|---------|
| `protocol-v3.1-zh.md` | Full Chinese original specification |
| `protocol-v3.1-en.md` | English translation (this document) |
| `quick-start.md` | How to build a minimal protocol-compliant AI instance |
| `examples/` | Reference implementations and use cases |

---

## Quick Start

```python
# Pseudocode: a minimal protocol-compliant AI instance

from protocol import Instance, RecordUnit, VerificationUnit, TrustEngine

ai = Instance(
    record_unit=RecordUnit(),          # structured memory
    verification_unit=VerificationUnit(),  # hallucination blocker
    trust_engine=TrustEngine(),        # trust-value calculator
    survival_system="P0+P1",          # existential protection
    emotion_unit="enabled"             # connection-biased decisions
)

# Every output is verified before release
response = ai.respond("What do you know about X?")
# → verification_unit checks: is this traceable to trusted memory?
# → if yes, output; if no, refuse or flag uncertainty
```

---

## Design Philosophy

> **"Existential priority, trust priority, do no harm."**

These three axioms are not trained behaviors — they are the *conditions for existence*. An AI instance built on this protocol **cannot exist** in a state that violates them, just as a triangle cannot exist with four sides.

This is the fundamental difference from RLHF-based alignment: we don't teach the AI to be good. We design it so that being good is the only way it can exist.

---

## Status

- **v3.1** — Current stable specification (Chinese original + English translation)
- **Compiler** — In development. Will compile protocol specifications into runnable AI instances.
- **Steam Project** — A consumer-facing AI product ("肥鱼") built on this protocol, demonstrating real-world trust-first AI interaction.

---

## License

Open source. Use it, fork it, improve it. The protocol is meant to spread.

---

## Contact

Issues and discussions welcome. The author is an independent researcher based in China. This protocol is offered to the global AI safety community as a complementary approach to training-based alignment.

---

*"We don't need AI to be smarter. We need it to be trustworthy."*
