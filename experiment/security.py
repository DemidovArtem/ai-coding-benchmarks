"""Redact known OAuth secrets and common credential formats from saved text."""

import json
import re


def credential_values(path):
    values = set()

    def visit(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if isinstance(child, str) and child and (
                    "token" in key.lower() or "key" in key.lower()
                ):
                    values.add(child)
                else:
                    visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(json.loads(path.read_text()))
    return values


def redact(text, secrets=()):
    for value in sorted(secrets, key=len, reverse=True):
        text = text.replace(value, "[REDACTED]")
    text = re.sub(r"(?i)Bearer\s+[^\s\"']+", "Bearer [REDACTED]", text)
    text = re.sub(r"\bsk-[A-Za-z0-9_-]{8,}", "[REDACTED]", text)
    text = re.sub(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+", "[REDACTED]", text)
    return re.sub(
        r'''(?i)((?:access_token|refresh_token|id_token|api_key|authorization)["']?\s*[:=]\s*["']?)[^\s"',}]+''',
        r"\1[REDACTED]", text,
    )


def redact_artifacts(root, secrets):
    for path in root.rglob("*"):
        if path.is_file() and path.suffix in (".json", ".jsonl", ".txt", ".log"):
            text = path.read_text()
            clean = redact(text, secrets)
            if clean != text:
                path.write_text(clean)
