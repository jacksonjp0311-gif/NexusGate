from __future__ import annotations

from pathlib import Path

from .bus import replay_message_bus
from .learn import replay_verify as learning_replay_verify
from .teach import replay_verify as teaching_replay_verify
from .verify import verify_model_replay


def replay_all(root: str | Path) -> dict:
    return verify_model_replay(root)
