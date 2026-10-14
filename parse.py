"""Turn data/2-call-records.md into calls.json (standard library only)."""
import json
import re
import sys
from pathlib import Path

HEADER = re.compile(r"^### (C-\d+) \| (\w+), (\d{1,2}:\d{2} [ap]m) \| (\d+) min (\d+) sec\s*$")
TURN = re.compile(r"^> \*\*(Assistant|Caller):\*\* ?(.*)$")
OUTCOME = re.compile(r"^Logged outcome: (.*)$")
CALL_LINE = re.compile(r"^(\d{2}:\d{2}:\d{2})\s+(\w+)\s+(.*)$")
RESULT_START = re.compile(r"^\s+->\s+(.*)$")


def parse_tool_log(lines):
    """Entries start at a timestamped line; '->' opens the result; any other
    indented line continues whichever of args/result is open."""
    entries, cur, target = [], None, None
    for line in lines:
        if not line.strip():
            continue
        m = CALL_LINE.match(line)
        if m:
            cur = {"time": m.group(1), "tool": m.group(2), "args": [m.group(3)], "result": []}
            entries.append(cur)
            target = "args"
            continue
        m = RESULT_START.match(line)
        if m and cur is not None:
            cur["result"].append(m.group(1))
            target = "result"
            continue
        if cur is not None:
            cur[target].append(line.strip())
    for e in entries:
        e["args"] = json.loads(" ".join(e["args"]))
        e["result"] = json.loads(" ".join(e["result"]))
    return entries


def parse(text):
    calls, cur, in_fence, fence = [], None, False, []
    for line in text.splitlines():
        m = HEADER.match(line)
        if m:
            cur = {
                "call_id": m.group(1),
                "day": m.group(2),
                "time": m.group(3),
                "duration_sec": int(m.group(4)) * 60 + int(m.group(5)),
                "transcript": [],
                "logged_outcome": None,
                "tool_log": [],
            }
            calls.append(cur)
            continue
        if cur is None:
            continue
        if line.startswith("```"):
            if in_fence:
                cur["tool_log"] = parse_tool_log(fence)
                fence = []
            in_fence = not in_fence
            continue
        if in_fence:
            fence.append(line)
            continue
        m = TURN.match(line)
        if m:
            cur["transcript"].append({"speaker": m.group(1), "text": m.group(2)})
            continue
        m = OUTCOME.match(line)
        if m:
            cur["logged_outcome"] = m.group(1).strip()
    return calls


def main(src="data/2-call-records.md", dst="calls.json"):
    calls = parse(Path(src).read_text(encoding="utf-8"))
    Path(dst).write_text(json.dumps(calls, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(calls)} calls to {dst}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
