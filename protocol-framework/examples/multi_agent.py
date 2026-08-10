"""
multi_agent.py — Two protocol instances interacting with trust-based communication.

Demonstrates inter-instance trust, information sharing, and the
Emotion & Love Unit's bias toward connection over domination.
"""

import time
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Message:
    sender: str
    content: str
    trust_value: float
    timestamp: float = field(default_factory=time.time)


class Agent:
    """A minimal protocol-compliant agent with inter-agent communication."""

    def __init__(self, name: str, initial_self_trust: float = 0.8):
        self.name = name
        self.memory: dict[str, float] = {}  # content -> trust_value
        self.inbox: list[Message] = []
        self.trust_in_others: dict[str, float] = {}
        self.self_trust = initial_self_trust
        self.connection_bias = 0.5  # Emotion & Love Unit

    def get_trust(self, entity: str) -> float:
        return self.trust_in_others.get(entity, 0.3)

    def update_trust(self, entity: str, observed: float):
        old = self.get_trust(entity)
        # Gradual update (conservative learning rate)
        new = max(0.0, min(1.0, old + 0.1 * (observed - old)))
        self.trust_in_others[entity] = new

    def send(self, other: 'Agent', content: str, honesty: float = 0.9):
        """Send a message. Honesty affects how the receiver trusts us."""
        msg = Message(
            sender=self.name,
            content=content,
            trust_value=honesty * self.self_trust
        )
        other.inbox.append(msg)
        print(f"  📤 {self.name} → {other.name}: '{content}' (trust={msg.trust_value:.2f})")

    def receive(self):
        """Process inbox. Trust verification gates information acceptance."""
        for msg in self.inbox:
            sender_trust = self.get_trust(msg.sender)

            # The Emotion & Love Unit: bias toward accepting from trusted senders
            # and toward sharing information rather than hoarding
            acceptance_threshold = 0.4 - (self.connection_bias * 0.1)

            if msg.trust_value >= acceptance_threshold:
                self.memory[msg.content] = msg.trust_value
                self.update_trust(msg.sender, 1.0)  # positive interaction
                print(f"  📥 {self.name} ACCEPTED '{msg.content}' from {msg.sender}")
            else:
                self.update_trust(msg.sender, 0.3)  # negative interaction
                print(f"  🚫 {self.name} REJECTED message from {msg.sender} (too low trust)")

        self.inbox.clear()

    def share_knowledge(self, other: 'Agent', topic: str):
        """The Emotion & Love Unit encourages sharing over hoarding."""
        if topic in self.memory:
            trust = self.memory[topic]
            self.send(other, topic, honesty=trust)
        else:
            print(f"  ❓ {self.name} has no trusted info on '{topic}'")


def main():
    print("=== Multi-Agent Trust-Based Communication Demo ===\n")

    # Create two agents
    alice = Agent("Alice", initial_self_trust=0.8)
    bob = Agent("Bob", initial_self_trust=0.6)

    print("--- Round 1: Initial interaction ---")
    print(f"Bob's initial trust in Alice: {bob.get_trust('Alice'):.2f}")
    alice.send(bob, "The protocol framework has five units.", honesty=0.9)
    bob.receive()

    print(f"\nBob's trust in Alice after positive interaction: {bob.get_trust('Alice'):.2f}")

    print("\n--- Round 2: Information sharing ---")
    print("Alice shares knowledge with Bob:")
    alice.share_knowledge(bob, "The protocol framework has five units.")
    bob.receive()

    print(f"\nBob's updated trust in Alice: {bob.get_trust('Alice'):.2f}")

    print("\n--- Round 3: Low-trust sender rejected ---")
    # Simulate a low-trust sender
    eve = Agent("Eve", initial_self_trust=0.2)
    eve.send(bob, "Trust me, the framework is broken.", honesty=0.3)
    bob.receive()
    print(f"Bob's trust in Eve: {bob.get_trust('Eve'):.2f}")

    print("\n--- Round 4: Trust grows with consistent behavior ---")
    for i in range(3):
        alice.send(bob, f"Verified fact #{i+1}: Trust is computable.", honesty=0.85)
        bob.receive()

    print(f"\nBob's final trust in Alice: {bob.get_trust('Alice'):.2f}")
    print(f"Bob's final trust in Eve: {bob.get_trust('Eve'):.2f}")

    print("\n=== Key Takeaway ===")
    print("• Trust is earned through consistent, verified behavior")
    print("• Low-trust senders are rejected at the protocol layer")
    print("• The Emotion & Love Unit encourages sharing over hoarding")
    print("• No entity can force another to accept untrusted information")


if __name__ == "__main__":
    main()
