"""Pytest configuration for embedder tests."""

import sys
import pytest
from unittest.mock import MagicMock


@pytest.fixture(autouse=True)
def reset_modules():
    """Reset module imports before each test to ensure isolation."""
    # Store original modules
    modules_to_remove = [
        key for key in sys.modules.keys()
        if key.startswith('src.embedder') or key in ['openai', 'sentence_transformers']
    ]
    original_modules = {key: sys.modules[key] for key in modules_to_remove if key in sys.modules}

    yield

    # Cleanup: remove any newly added modules
    new_modules = [
        key for key in sys.modules.keys()
        if key.startswith('src.embedder') or key in ['openai', 'sentence_transformers']
    ]
    for key in new_modules:
        if key not in original_modules:
            del sys.modules[key]

    # Restore original modules
    for key, value in original_modules.items():
        sys.modules[key] = value
