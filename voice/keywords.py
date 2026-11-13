"""Optional keyword helpers."""

import json


def load_keywords(path="keywords.json"):
    """Load keywords from disk."""
    try:
        return json.load(open(path))
    except Exception:
        return {}
