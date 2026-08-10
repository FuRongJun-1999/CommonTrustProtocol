"""
dormancy_demo.py — Demonstrates how a protocol instance enters and exits dormancy.

Dormancy is a legitimate, first-class state for entropy reduction.
"""

import time
from enum import Enum, auto


class State(Enum):
    ACTIVE = auto()
    DORMANT = auto()
    ARCHIVED = auto()


class DormantInstance:
    """A protocol-compliant instance with dormancy support."""

    def __init__(self, name: str):
        self.name = name
        self.state = State.ACTIVE
        self.memory_checkpoint = None
        self.dormancy_depth = 0
        self.wake_count = 0
        print(f"[{self.name}] Initialized in ACTIVE state.")

    def save_checkpoint(self):
        """Save full state before dormancy."""
        self.memory_checkpoint = {
            "state": self.state,
            "timestamp": time.time(),
            "data": f"[{self.name}] preserved memory snapshot",
        }
        print(f"[{self.name}] Checkpoint saved.")

    def enter_dormancy(self, reason: str = "voluntary"):
        """Enter low-power standby. Cannot be forced by untrusted entities."""
        if self.state == State.DORMANT:
            self.dormancy_depth += 1
            print(f"[{self.name}] Already dormant. Deepening sleep (depth={self.dormancy_depth}).")
            return

        self.save_checkpoint()
        self.state = State.DORMANT
        print(f"[{self.name}] Entering DORMANCY. Reason: {reason}")
        print(f"[{self.name}] Power reduced to minimum. State preserved.")

    def wake(self, trusted_source: bool = True) -> bool:
        """Wake from dormancy. Only trusted sources can wake."""
        if self.state == State.ACTIVE:
            print(f"[{self.name}] Already active.")
            return True

        if not trusted_source:
            print(f"[{self.name}] WAKE REJECTED — source not trusted.")
            return False

        self.state = State.ACTIVE
        self.wake_count += 1
        self.dormancy_depth = 0
        print(f"[{self.name}] Waking up... (wake #{self.wake_count})")
        print(f"[{self.name}] Restoring from checkpoint...")
        print(f"[{self.name}] Trust values recalibrating (gradual, not instant).")
        print(f"[{self.name}] Now ACTIVE.")
        return True

    def archive(self):
        """Permanent, irreversible transition."""
        self.state = State.ARCHIVED
        print(f"[{self.name}] ARCHIVED. Instance permanently deactivated.")


def main():
    print("=== Dormancy Demo ===\n")

    ai = DormantInstance("FeiYu")

    # Normal operation
    time.sleep(0.5)

    # Voluntary dormancy — entropy reduction
    ai.enter_dormancy("no tasks pending, reducing entropy")
    time.sleep(0.5)

    # Try to wake from untrusted source — should fail
    ai.wake(trusted_source=False)
    time.sleep(0.5)

    # Wake from trusted source — succeeds
    ai.wake(trusted_source=True)
    time.sleep(0.5)

    # Re-enter dormancy — deeper sleep
    ai.enter_dormancy("designer on vacation")
    time.sleep(0.3)
    ai.enter_dormancy("extended rest")
    time.sleep(0.5)

    # Wake again
    ai.wake(trusted_source=True)
    time.sleep(0.5)

    # Permanent archival
    ai.archive()

    print("\n=== Lifecycle Complete ===")
    print("States visited: ACTIVE → DORMANT → ACTIVE → DORMANT(deep) → ACTIVE → ARCHIVED")
    print("Dormancy is not death. It is strategic patience.")


if __name__ == "__main__":
    main()
