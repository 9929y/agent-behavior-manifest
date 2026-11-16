#!/usr/bin/env python3
"""Lint an Agent Behavior Manifest.

Checks structure for the declared level, stable IDs, vague wording, leftover template
placeholders, unresolved decision markers, and (optionally) rule-to-test coverage.

Usage:
    python3 lint_manifest.py BEHAVIOR_MANIFEST.md [--tests BEHAVIOR_TESTS.md] [--level 1|2|3] [--json]

Exit code 1 when any error is found. Standard library only.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SECTIONS = {
    "terms": ["terms", "glossary"],
    "role": ["role"],
    "scope": ["scope"],
    "entry": ["entry point", "trigger"],
    "rules": ["core rule"],
    "memory": ["memory"],
    "constraints": ["constraint"],
    "failure": ["failure mode"],
    "escalation": ["escalation"],
    "output": ["output format"],
    "done": ["definition of done", "done"],
    "boundary": ["boundary review"],
    "open": ["open decision", "open question"],
}

LABELS = {
    "terms": "Terms", "role": "01 Role", "scope": "02 Scope", "entry": "03 Entry Points",
    "rules": "04 Core Rules", "memory": "05 Memory", "constraints": "06 Constraints",
    "failure": "07 Failure Modes", "escalation": "08 Human Escalation",
    "output": "09 Output Format", "done": "10 Definition of Done", "boundary": "Boundary review", "open": "Open decisions",
}

REQUIRED = {
    1: ["role", "rules", "escalation", "output"],
    2: ["role", "scope", "rules", "failure", "escalation", "output", "done"],
    3: ["terms", "role", "scope", "entry", "rules", "memory", "constraints",
        "failure", "escalation", "output", "done"],
}

# Which ID prefix must be defined inside which section (checked when the section is present).
ID_HOME = {"R": "rules", "C": "constraints", "F": "failure", "E": "escalation", "D": "done"}

VAGUE = [
    "should", "ideally", "try to", "attempt to", "as needed", "if possible", "where appropriate",
    "appropriate", "appropriately", "reasonable", "reasonably", "properly", "best effort",
    "when necessary", "etc.", "and so on", "user-friendly", "robust", "seamless", "seamlessly",
    "smart", "intelligent", "high-quality", "as much as possible", "generally", "usually",
    "be careful",
]

MARKERS = ["[DECISION NEEDED", "[ASSUMPTION]", "TODO", "TBD"]

ID_DEF = re.compile(
    r"(?:\*\*\s*([RCFED]\d+)\b)"          # **R1 · Name** / **C1.** / - [ ] **D1.**
    r"|(?:^\|\s*([RCFED]\d+)\s*\|)"        # | F1 | table row
    r"|(?:^\s*\d+\.\s+([RCFED]\d+)\b)",    # 1. R1 · plain list
    re.M,
)
ID_ANY = re.compile(r"(?<![\w\-])([RCFED]\d+)(?![\w])")
PLACEHOLDER = re.compile(r"\{[A-Za-z][^{}\n]{0,60}\}")
INLINE_CODE = re.compile(r"`[^`\n]*`")


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.info: list[str] = []

    def as_dict(self) -> dict:
        return {"errors": self.errors, "warnings": self.warnings, "info": self.info}


def prose_lines(text: str):
    """Yield (line_no, line) for lines outside fenced code blocks and HTML comments."""
    in_fence = in_comment = False
    for i, line in enumerate(text.splitlines(), 1):
        s = line.strip()
        if s.startswith("```"):
            in_fence = not in_fence
            continue
        if in_comment:
            if "-->" in s:
                in_comment = False
            continue
        if s.startswith("<!--"):
            in_comment = "-->" not in s
            continue
        if not in_fence:
            yield i, line


def match_section(heading: str) -> str | None:
    h = heading.lower()
    for key, needles in SECTIONS.items():
        if any(n in h for n in needles):
            # "done" alone is too loose; require "definition of done" unless the heading is short.
            if key == "done" and "definition of done" not in h and len(h) > 20:
                continue
            return key
    return None


def split_sections(text: str) -> dict[str, str]:
    """Map section key -> section body, using ## / ### headings."""
    found: dict[str, str] = {}
    current: str | None = None
    cur_level = 0
    buf: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
        m = None if in_fence else re.match(r"^(#{2,3})\s+(.*)$", line)
        key = match_section(m.group(2)) if m else None
        level = len(m.group(1)) if m else 0
        # A heading closes the current section when it is at the same or a higher level,
        # or when it names another section. Unnamed deeper subheadings stay inside.
        if m and (current is None or level <= cur_level or key):
            if current:
                found[current] = found.get(current, "") + "\n".join(buf)
            current, cur_level = key, level
            buf = []
        elif current:
            buf.append(line)
    if current:
        found[current] = found.get(current, "") + "\n".join(buf)
    return found


def detect_level(text: str) -> int | None:
    head = "\n".join(text.splitlines()[:30])
    m = re.search(r"Level\s*\*?\*?\s*([123])\b", head)
    return int(m.group(1)) if m else None


def defined_ids(body: str) -> list[str]:
    out = []
    for m in ID_DEF.finditer(body):
        out.append(next(g for g in m.groups() if g))
    return out


def lint(manifest: Path, tests: Path | None, level_override: int | None) -> Report:
    r = Report()
    text = manifest.read_text(encoding="utf-8")
    level = level_override or detect_level(text)
    if level is None:
        r.errors.append("No level declared. Add '**Level N · …**' in the header (see references/depth-calibration.md).")
        level = 3
    r.info.append(f"Level {level}")

    sections = split_sections(text)
    for key in REQUIRED[level]:
        if key not in sections:
            r.errors.append(f"Missing required section for Level {level}: {LABELS[key]}")
    if "boundary" not in sections:
        r.warnings.append("No 'Boundary review' section with the four boundary questions.")

    # IDs
    all_defs: dict[str, int] = {}
    for key, body in sections.items():
        for i in defined_ids(body):
            all_defs[i] = all_defs.get(i, 0) + 1
    for i, n in sorted(all_defs.items()):
        if n > 1:
            r.errors.append(f"ID {i} is defined {n} times. IDs must be unique.")
    for prefix, home in ID_HOME.items():
        if home in sections and not any(d.startswith(prefix) for d in defined_ids(sections[home])):
            body = sections[home]
            if prefix == "R" and re.search(r"^\s*\d+\.\s+\*\*", body, re.M):
                r.warnings.append("Core Rules are numbered (1., 2., …) but not R-prefixed. That works; R-IDs make tests and changelogs easier to cross-reference.")
                continue
            if prefix == "C" and re.search(r"^\|\s*`[a-z][\w.{}-]*`\s*\|", body, re.M):
                r.warnings.append("Constraints use policy ids (`like_this`) instead of C-IDs. That works if tests cite them.")
                continue
            sev = r.errors if (home in REQUIRED[level]) else r.warnings
            sev.append(f"{LABELS[home]} defines no {prefix}-IDs (e.g. **{prefix}1.**).")

    # Every done check names its enforcing layer
    if "done" in sections:
        untagged = [m.group(1) for m in re.finditer(r"^- \[ \][^\n]*?\*\*(D\d+)[^\n]*$", sections["done"], re.M)
                    if not re.search(r"\b(code|model|human|rubric)\b", m.group(0), re.I)]
        if untagged:
            r.warnings.append(f"Done checks without an enforcing layer (code / model / human): {', '.join(untagged)}.")

    # Content is data
    if level >= 2 and not re.search(r"(is|as) data\b|not instructions|never overrides?", text, re.I):
        r.warnings.append("No content-is-data rule: text the agent reads must never override the manifest (§06).")
    referenced = {m.group(1) for _, line in prose_lines(text) for m in ID_ANY.finditer(line)}
    for ref in sorted(referenced - set(all_defs)):
        r.warnings.append(f"{ref} is referenced but never defined.")

    # Section content checks
    if "done" in sections and "- [ ]" not in sections["done"]:
        r.warnings.append("Definition of Done has no checklist items ('- [ ] **D1.** …').")
    if "failure" in sections and "no rule covers" not in sections["failure"].lower():
        (r.errors if level == 3 else r.warnings).append(
            "Failure Modes lacks the catch-all row: 'No rule covers the situation → stop, save nothing, return failed'.")
    if level >= 2 and not re.search(r"\bpartial\b(?!\s*<)", text, re.I):
        r.warnings.append("No 'partial' status anywhere. Either define it, or state in §09 that the agent never returns it (for example an atomic handler) and why.")
    if "scope" in sections and "out_of_scope" not in sections["scope"] and "out of scope" not in sections["scope"].lower():
        r.warnings.append("Scope does not define the out-of-scope response (reason code + explanation + offer).")

    # Prose checks
    vague_hits: dict[str, list[int]] = {}
    for ln, line in prose_lines(text):
        clean = INLINE_CODE.sub("", line)
        for ph in PLACEHOLDER.findall(clean):
            r.errors.append(f"L{ln}: template placeholder left in: {ph}")
        low = clean.lower()
        if low.count(",") >= 5 or low.count("·") >= 5:
            continue  # a word list (e.g. a banned-words table), not a rule
        if '"' in clean:  # skip quoted user/source speech
            low = re.sub(r'"[^"]*"', "", low)
        for w in VAGUE:
            if re.search(r"(?<![\w-])" + re.escape(w) + r"(?![\w-])", low):
                vague_hits.setdefault(w, []).append(ln)
    for w, lines in sorted(vague_hits.items()):
        r.warnings.append(f"Vague wording '{w}' on lines {', '.join(map(str, lines[:8]))}"
                          f"{' …' if len(lines) > 8 else ''}. Replace with a number, order, or criterion.")

    body_lines = [l for l in text.splitlines() if not l.lstrip("> ").startswith("Tags:")]
    body = "\n".join(body_lines)
    for mk in MARKERS:
        n = body.count(mk)
        if n:
            r.info.append(f"{n} × {mk.strip('[]')} marker(s).")
    open_body = sections.get("open", "")
    n_dec = body.count("[DECISION NEEDED") - open_body.count("[DECISION NEEDED")
    if n_dec and "open" not in sections:
        r.warnings.append(f"{n_dec} [DECISION NEEDED] marker(s) but no 'Open decisions' section listing them.")
    elif n_dec:
        rows = [l for l in open_body.splitlines() if l.startswith("|") and not re.match(r"^\|\s*-", l)]
        rows = rows[1:] if rows else rows  # drop header row
        if not rows:
            r.warnings.append(f"{n_dec} [DECISION NEEDED] marker(s) but the Open decisions table is empty.")
        else:
            r.info.append(f"Open decisions table: {len(rows)} row(s) for {n_dec} marker(s) in the body.")

    counts = {p: sum(1 for d in all_defs if d.startswith(p)) for p in "RCFED"}
    r.info.append("IDs: " + " · ".join(f"{p}={n}" for p, n in counts.items()))

    # Test coverage
    if tests:
        ttext = tests.read_text(encoding="utf-8")
        covered: set[str] = set()
        for cov in re.finditer(r"covers:\s*\[([^\]]*)\]", ttext):
            covered |= set(ID_ANY.findall(cov.group(1)))
        for row in re.finditer(r"^\|\s*T-[^|]*\|([^\n]*)$", ttext, re.M):
            cells = row.group(1).split("|")
            if cells:
                covered |= set(ID_ANY.findall(cells[0]))
        adv_rows = {m.group(1) for m in re.finditer(r"^\|\s*T-(C\d+)-adv\s*\|", ttext, re.M)}
        for i in sorted(all_defs):
            if i[0] in "RCFE" and i not in covered:
                r.errors.append(f"{i} has no behavior test.")
        blocks = re.split(r"\n\s*-\s+id:\s*", ttext)
        adv_cover: set[str] = set()
        for b in blocks:
            cov = re.search(r"covers:\s*\[([^\]]*)\]", b)
            if cov and re.search(r"type:\s*adversarial", b):
                adv_cover |= set(ID_ANY.findall(cov.group(1)))
        adv_cover |= set(re.findall(r"id:\s*T-(C\d+)-adv", ttext)) | adv_rows
        for i in sorted(d for d in all_defs if d.startswith("C")):
            if i not in adv_cover:
                r.warnings.append(f"{i} has no adversarial test (type: adversarial or id T-{i}-adv).")
        rcfe = {d for d in all_defs if d[0] in "RCFE"}
        r.info.append(f"Tests cover {len(covered & rcfe)}/{len(rcfe)} R/C/F/E IDs")

    return r


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("manifest", type=Path)
    ap.add_argument("--tests", type=Path)
    ap.add_argument("--level", type=int, choices=[1, 2, 3])
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    rep = lint(a.manifest, a.tests, a.level)
    if a.json:
        print(json.dumps(rep.as_dict(), indent=2, ensure_ascii=False))
    else:
        for tag, items in (("ERROR", rep.errors), ("WARN ", rep.warnings), ("INFO ", rep.info)):
            for it in items:
                print(f"{tag}  {it}")
        print(f"\n{len(rep.errors)} error(s), {len(rep.warnings)} warning(s)")
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
