"""Text cleaning: normalize whitespace, drop noise, keep content intact."""
import re


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    lines = [line.strip() for line in text.split("\n")]
    # Drop single-character noise lines (e.g. stray page artefacts).
    lines = [ln for ln in lines if len(ln) > 1 or ln == ""]
    cleaned = "\n".join(lines)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    return cleaned
