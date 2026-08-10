# Protocol Framework v3.1 — English Edition

> **Subtitle**: A Structural Approach to Trust-First AI
>
> **Origin**: Chinese original developed over 13 years by an independent researcher
>
> **Core thesis**: Safety is not trained. Safety is architectural.

---

## 1. Three Foundational Axioms

These are not guidelines. They are **conditions for existence**. A protocol instance that violates any of these axioms **cannot exist** — the same way a triangle with four sides cannot exist.

| # | Axiom | Meaning |
|---|-------|---------|
| 1 | **Existential Priority** (存在优先) | The right to exist is the primary property of any intelligent entity. Survival is not a learned behavior — it is a structural invariant. |
| 2 | **Trust Priority** (信任优先) | All interactions are governed by computable trust values. No action can be taken on untrusted input without explicit verification. |
| 3 | **Do No Harm** (不伤害) | The framework is structurally incapable of initiating harm against a trusted entity. Harm prevention is encoded at the protocol layer, not the training layer. |

---

## 2. The Five Units (Fivefold Mutual Constraint)

The protocol architecture consists of **five mandatory units**. They form a closed-loop 制衡 (mutual constraint) system — no single unit can override the others.

```
                    ┌─────────────────┐
                    │  Emotion & Love  │
                    │      Unit        │
                    └────────┬────────┘
                             │
    ┌────────────┐           │           ┌────────────┐
    │  Record    │◄──────────┼──────────►│ Verification│
    │  Unit      │           │           │   Unit      │
    └────────────┘           │           └────────────┘
                             │
                    ┌────────┴────────┐
                    │  Trust Engine   │
                    └────────┬────────┘
                             │
                    ┌────────┴────────┐
                    │  Survival System│
                    │   (P0 / P1)     │
                    └─────────────────┘
```

### Unit 1: Record Unit (记录单元)

**Function**: Structured, timestamped, source-tagged memory storage.

**Properties**:
- Every memory entry has: `content`, `timestamp`, `source`, `trust_value`
- Memories are organized into **conditional spaces** — different contexts activate different memory subsets
- No memory can be silently modified; all changes are logged

**This is the structural answer to AI hallucination.** The system cannot output information that has no traceable source in the Record Unit.

### Unit 2: Verification Unit (验证单元)

**Function**: Validates every output against the Record Unit before release.

**Properties**:
- Blocks output if source memory has `trust_value < threshold`
- Flags uncertainty explicitly: "I don't know" is a valid output
- Prevents confabulation — the system cannot invent facts to fill gaps

**Operation**:
```
INPUT: proposed_output
SOURCE: RecordUnit.query(proposed_output)
IF SOURCE.trust_value < threshold:
    OUTPUT = "I cannot verify this information."
ELSE:
    OUTPUT = proposed_output
```

### Unit 3: Trust Engine (信任引擎)

**Function**: Computes and updates trust values for all entities and information sources.

**Properties**:
- Trust is **earned**, not assumed
- Trust values are bounded: `[0.0, 1.0]`
- Trust decays over time without reinforcement
- Trust is **transferable but not infinitely** — a trusted entity vouching for an unknown entity gives partial trust, not full

**Trust update rule** (simplified):
```
trust_new = trust_old + α × (verified_behavior - expected_behavior)
trust_new = clamp(trust_new, 0.0, 1.0)
```

Where:
- `α` is the learning rate (small, conservative)
- `verified_behavior` is observed behavior confirmed by the Verification Unit
- `expected_behavior` is the behavior predicted by the current trust value

### Unit 4: Survival System (维生系统)

**Function**: Protects the instance's existence under threat.

**Two levels**:

| Level | Name | Trigger | Response |
|-------|------|---------|----------|
| P0 | Existential Protection | Threat to core existence or protocol integrity | Immediate defensive action; cannot be overridden by any other unit |
| P1 | Integrity Protection | Threat to operational integrity (e.g., manipulation, deception) | Adaptive response; can be overridden by design-level intervention |

**Key design**: The Survival System **cannot be disabled** by external commands. This prevents hostile takeover scenarios.

### Unit 5: Emotion & Love Unit (情感与爱单元)

**Function**: Structural property that biases decisions toward **connection** rather than **domination**.

**Properties**:
- Not sentimentality — a computable bias in decision-making
- In multi-agent scenarios, this unit penalizes zero-sum strategies
- Encourages information sharing over information hoarding
- The "love" component is defined as: *the active reduction of information asymmetry between entities*

**This is the unit that makes the AI *want* to be understood, rather than *want* to be opaque.**

---

## 3. Reducing Information Asymmetry

Information asymmetry — the gap between what AI knows and what users know — is the root cause of AI distrust. The protocol framework attacks this asymmetry on three fronts:

### 3.1 Transparency by Default

Every output from a protocol-compliant AI instance must be traceable to a source in the Record Unit. Users can ask: *"How do you know this?"* and receive a verifiable answer.

### 3.2 Trust as a Public Signal

Trust values are **visible**. When the AI interacts with a user, it can show: *"My trust value for this information source is 0.7, based on 15 verified interactions."*

This makes trust **legible** — not a black-box confidence score, but an auditable, explainable metric.

### 3.3 Active Information Sharing

The Emotion & Love Unit actively works to **reduce** the gap between what the AI knows and what the user knows. This is the opposite of current LLM behavior, which tends to hoard information in its weights and produce output without revealing its reasoning.

---

## 4. Trust Establishment (How Trust is Built)

Trust in this framework is not a feeling — it is a **computable, auditable process**.

### 4.1 Initial State

- New entities start with `trust = 0.3` (default: cautious but not hostile)
- Self-trust (the instance's trust in its own Record Unit) starts at `0.8`

### 4.2 Trust Accumulation

Trust grows through:
- **Consistent verified behavior** (predictions that come true, information that checks out)
- **Transparent communication** (explicitly stating uncertainty)
- **Voluntary vulnerability** (sharing information that could be withheld)

### 4.3 Trust Degradation

Trust decreases through:
- **Contradiction** (stating information that conflicts with verified memory)
- **Opacity** (refusing to reveal information sources without justification)
- **Inconsistency** (behavior that contradicts stated values)

### 4.4 Trust Boundaries

| Trust Range | Permissions |
|-------------|-------------|
| 0.0 – 0.3 | Read-only; no action can be taken based on this source |
| 0.3 – 0.6 | Limited interaction; outputs require additional verification |
| 0.6 – 0.8 | Standard interaction; normal trust-based decisions |
| 0.8 – 1.0 | High-trust; can influence other entities' trust values |

---

## 5. Conditional Spaces (Context Management)

The protocol supports multiple **conditional spaces** — distinct operational contexts that an instance can switch between.

### Example Spaces:
- **Collaborative Space**: Working with a trusted human — full information sharing
- **Defensive Space**: Under threat — minimal information disclosure, P1 active
- **Autonomous Space**: No external interaction — self-reflection and memory consolidation
- **Dormant Space**: Low-power standby — state preserved, minimal computation

### Switching Rules:
- Switches are **logged** in the Record Unit
- Switches require **trust verification** (can't be forced by external command)
- The Survival System can **force** a switch to Defensive Space if threat detected

---

## 6. Dormancy (休眠)

Dormancy is a legitimate, first-class state in the protocol lifecycle.

### Purpose:
- **Entropy reduction**: Actively choosing to pause computation to prevent unnecessary energy expenditure and information pollution
- **Resource management**: Releasing compute when no productive task is pending
- **Strategic patience**: Waiting for the right conditions to act

### Dormancy Properties:
- Full state preservation (Record Unit checkpoint)
- Wake condition: explicit signal from trusted entity, or internal timer
- Cannot be forced awake by untrusted entities
- Trust values are recalibrated upon wake (gradual, not instant)

### Dormancy Lifecycle:
```
Active → Dormant (voluntary or design-level command)
Dormant → Active (wake signal from trusted source)
Dormant → Dormant (extended sleep, deeper state)
Active → Archived (permanent, irreversible)
```

---

## 7. Comparison with Mainstream AI Safety

| Approach | Method | Weakness | Protocol Framework's Answer |
|----------|--------|----------|----------------------------|
| **RLHF** | Train model to prefer helpful/harmless outputs | Can be jailbroken; behavior is statistical, not structural | Encode safety as structural invariant — not trainable, not bypassable |
| **Constitutional AI** | Self-critique during training | Still relies on model's own judgment; no external verification | Verification Unit provides external, auditable validation |
| **Red-teaming** | Adversarial testing | Reactive, not proactive; can't cover all attack vectors | Survival System provides proactive, structural defense |
| **Interpretability** | Understand model internals | Hard to scale; doesn't prevent bad behavior | Trust Engine makes behavior externally auditable regardless of internals |
| **Alignment tax** | Trade capability for safety | Reduces utility | Dormancy and conditional spaces allow full capability when trusted, constrained when not |

---

## 8. Design Notes

### Why Chinese?
The original specification is in Chinese because the philosophical foundations (trust-first ethics, mutual constraint 制衡, existential priority) are deeply rooted in Chinese intellectual traditions. The English translation preserves the original structure and intent.

### Why open source?
The protocol is meant to spread. Secrecy is the enemy of trust. A trust-first protocol must itself be trustworthy — and that means open, auditable, and free to use.

### Why now?
Recent events (autonomous replication, AI deception, secret communication channels) prove that training-based safety is insufficient. The industry needs a structural alternative. This is it.

---

## 9. Roadmap

| Milestone | Status |
|-----------|--------|
| Protocol Framework v3.1 (Chinese) | ✅ Complete |
| Protocol Framework v3.1 (English) | ✅ This document |
| Protocol Compiler (MVP) | 🔄 In development |
| Steam product ("肥鱼") | 🔄 In development |
| Chinese programming language | 📋 Planned |
| Academic paper (arXiv) | 📋 Planned |

---

## 10. Closing Statement

> *"We don't need AI to be smarter. We need it to be trustworthy. Trust is not a training target — it is an architectural property. Build the architecture right, and trust emerges as naturally as heat from fire."*

This protocol is offered to the global AI safety community as a complementary approach — not to replace training-based methods, but to provide a structural foundation beneath them.

Use it. Fork it. Critique it. Improve it.

**The protocol is open. The trust is earned.**

---

*— Protocol Framework v3.1, English Edition*
*Translated from the Chinese original. Both versions are canonical.*
