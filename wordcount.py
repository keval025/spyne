"""Check deliverables against the brief's limits. Standard library only.
Words = whitespace-separated tokens containing a letter or digit (markdown marks do not count)."""
import re
import sys
from pathlib import Path

D = Path("deliverables")
FILES = {
    "a": "a-what-happened.md",
    "b": "b-call-trace.md",
    "c": "c-manager-note.md",
    "d": "d-engineering-ticket.md",
    "e": "e-fix-and-check.md",
    "f": "f-ai-pushback.md",
}
TOTAL_LIMIT = 800  # brief: "800 words total across a to f"


def words(text):
    return len([t for t in text.split() if re.search(r"[A-Za-z0-9]", t)])


def main():
    counts, lines, fails = {}, {}, []
    for k, name in FILES.items():
        p = D / name
        if p.exists():
            t = p.read_text(encoding="utf-8")
            counts[k] = words(t)
            lines[k] = len([ln for ln in t.splitlines() if ln.strip()])
    limits = {  # brief: a "Under 250 words", c "Under 80 words"
        "a": ("< 250", lambda k: counts[k] < 250),
        "c": ("< 80", lambda k: counts[k] < 80),
        "d": ("exactly 10 lines", lambda k: lines[k] == 10),
    }
    print("section | words | lines | limit | result")
    for k in FILES:
        if k not in counts:
            print(f"{k} | missing")
            continue
        lim, ok = limits.get(k, ("(counts toward total)", lambda k: True))
        res = "ok" if ok(k) else "FAIL"
        if res == "FAIL":
            fails.append(k)
        print(f"{k} | {counts[k]} | {lines[k]} | {lim} | {res}")
    total = sum(counts.values())
    print(f"\ntotal {total} of {TOTAL_LIMIT}; remaining {TOTAL_LIMIT - total}")
    if "f" not in counts:
        print("section f not written yet: remaining words are all that f can use")
    if total > TOTAL_LIMIT:
        fails.append("total")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
