from __future__ import annotations

"""
Schedule prediction agent.

Parses the quarterly schedule PDFs in Schedules/ and builds a frequency index
of which quarters each course has historically appeared in. Used to supplement
RAG answers with a "when might this course be offered?" note.
"""
import re
from collections import defaultdict
from pathlib import Path

from pypdf import PdfReader

from config import SCHEDULES_DIR

# Quarter labels for display
QUARTER_LABELS = {"AUT": "Autumn", "WIN": "Winter", "SPR": "Spring", "SUM": "Summer"}

# Only match known Foster MBA subject prefixes to avoid false positives
COURSE_CODE_RE = re.compile(
    r"\b(FIN|MKTG|ENTRE|ACCT|ACCTG|OPMGT|MGMT|IBUS|QMETH)\s*(\d{3,4})\b",
    re.IGNORECASE,
)

# Filename substrings that mean the PDF covers multiple quarters — skip for per-quarter counting
MULTI_QUARTER_MARKERS = ["year-at-a-glance", "year at a glance"]


def _detect_quarter(filename: str) -> str | None:
    lower = filename.lower()
    if any(marker in lower for marker in MULTI_QUARTER_MARKERS):
        return None
    for quarter in QUARTER_LABELS:
        if quarter.lower() in lower:
            return quarter
    return None


def _extract_course_codes(text: str) -> set[str]:
    codes = set()
    for match in COURSE_CODE_RE.finditer(text):
        dept = match.group(1).upper()
        # Normalise ACCTG → ACCT so codes stay consistent with syllabus filenames
        if dept == "ACCTG":
            dept = "ACCT"
        codes.add(f"{dept} {match.group(2)}")
    return codes


def _build_index() -> dict[str, dict[str, int]]:
    """Return {course_code: {quarter: count}} from all quarterly schedule PDFs."""
    index: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    if not SCHEDULES_DIR.exists():
        return {}

    for pdf_path in sorted(SCHEDULES_DIR.glob("*.pdf")):
        quarter = _detect_quarter(pdf_path.name)
        if not quarter:
            continue
        try:
            reader = PdfReader(str(pdf_path))
            text = " ".join(page.extract_text() or "" for page in reader.pages)
        except Exception:
            continue
        for code in _extract_course_codes(text):
            index[code][quarter] += 1

    return {k: dict(v) for k, v in index.items()}


# Module-level cache — built once on first call, reused for all subsequent requests
_index: dict[str, dict[str, int]] | None = None


def _get_index() -> dict[str, dict[str, int]]:
    global _index
    if _index is None:
        _index = _build_index()
    return _index


def extract_codes_from_chunks(titles_and_filenames: list[tuple[str, str]]) -> list[str]:
    """Extract unique course codes from a list of (title, filename) pairs."""
    codes: set[str] = set()
    for title, filename in titles_and_filenames:
        codes |= _extract_course_codes(f"{title} {filename}")
    return sorted(codes)


def predict_offerings(course_codes: list[str]) -> str | None:
    """
    Given a list of course codes, return a natural-language schedule prediction
    string, or None if no historical data is found for any of the codes.
    """
    if not course_codes:
        return None

    index = _get_index()
    lines: list[str] = []

    for code in course_codes:
        quarters = index.get(code)
        if not quarters:
            continue
        sorted_q = sorted(quarters.items(), key=lambda x: x[1], reverse=True)
        parts = [f"{QUARTER_LABELS[q]} ({n}×)" for q, n in sorted_q]
        most_likely = QUARTER_LABELS[sorted_q[0][0]]
        lines.append(
            f"• {code}: seen in {', '.join(parts)} — most likely **{most_likely}**"
        )

    if not lines:
        return None

    header = "Based on past Foster MBA schedules (2024–2026):"
    return header + "\n" + "\n".join(lines)
