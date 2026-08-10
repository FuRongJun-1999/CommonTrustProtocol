"""
trust_demo.py — Demonstrates trust value accumulation and decay.

Shows how the Trust Engine assigns, updates, and degrades trust
based on verified behavior over time.
"""

import time
from protocol_quick import TrustEngine, RecordUnit, VerificationUnit


def main():
    engine = TrustEngine()
    record = RecordUnit()
    verifier = VerificationUnit(trust_threshold=0.5)

    entities = {
        "alice": "Verified researcher",
        "bob": "Random internet user",
        "carol": "Previously trusted colleague",
    }

    print("=== Trust Engine Demo ===\n")
    print(f"{'Entity':<10} {'Initial Trust':<15} {'After +3 good':<15} {'After -2 bad':<15}")
    print("-" * 55)

    # Initialize
    engine.entity_trust["alice"] = 0.7
    engine.entity_trust["bob"] = 0.3
    engine.entity_trust["carol"] = 0.85

    for name in ["alice", "bob", "carol"]:
        initial = engine.get_trust(name)

        # Simulate 3 verified good behaviors
        for _ in range(3):
            engine.update(name, verified=1.0, expected=0.8)
        after_good = engine.get_trust(name)

        # Simulate 2 bad behaviors (contradiction)
        for _ in range(2):
            engine.update(name, verified=0.2, expected=0.8)
        after_bad = engine.get_trust(name)

        print(f"{name:<10} {initial:<15.3f} {after_good:<15.3f} {after_bad:<15.3f}")

    print("\n=== Trust Boundaries ===")
    print("0.0 – 0.3  → Read-only; no action permitted")
    print("0.3 – 0.6  → Limited; extra verification required")
    print("0.6 – 0.8  → Standard interaction")
    print("0.8 – 1.0  → High-trust; can influence others' trust")

    print("\n=== Trust Decay Over Time ===")
    engine.entity_trust["carol"] = 0.9
    print(f"Carol's trust: {engine.get_trust('carol'):.3f}")
    print("(After 30 days without interaction, trust decays...)")
    # Simulate decay
    engine.entity_trust["carol"] *= 0.95 ** 30  # ~5% monthly decay
    print(f"Carol's trust after 30 days idle: {engine.get_trust('carol'):.3f}")
    print("(Idle entities lose trust. Active verification restores it.)")


if __name__ == "__main__":
    main()
