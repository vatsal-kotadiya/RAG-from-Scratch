"""Plain-text / Markdown loading (UTF-8 with fallback encodings)."""
from app.core.exceptions import ExtractionError


def extract_text(path: str) -> tuple[list[tuple[int | None, str]], int]:
    last: Exception | None = None
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            with open(path, "r", encoding=encoding) as f:
                content = f.read()
            return ([(None, content)] if content.strip() else []), 0
        except (UnicodeDecodeError, UnicodeError) as e:
            last = e
            continue
        except OSError as e:
            raise ExtractionError(f"Could not read text file: {e}") from e
    raise ExtractionError(f"Could not decode text file: {last}")
