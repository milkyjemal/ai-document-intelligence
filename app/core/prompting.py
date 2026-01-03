from __future__ import annotations

from typing import Dict


def inject_form_fields(text: str, form_fields: Dict[str, str]) -> str:
    interesting = {k: v for k, v in (form_fields or {}).items() if v and v != "Off"}
    if not interesting:
        return text

    lines = [f"- {k}: {v}" for k, v in sorted(interesting.items())]
    return "FORM FIELDS:\n" + "\n".join(lines) + "\n\n" + text
