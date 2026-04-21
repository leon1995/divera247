"""Shared helpers for v2 endpoint fixture tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

V2_FIXTURE_DIR = Path(__file__).resolve().parent
EXAMPLE_ID = 123
EXAMPLE_FOREIGN_ID = 'de1234000000abcdefga00'


def load_v2_json(directory: str, filename: str) -> Any:
    """Load a JSON fixture from ``tests/v2/<directory>/``."""
    path = V2_FIXTURE_DIR / directory / filename
    return json.loads(path.read_text(encoding='utf-8'))
