"""Recompute the weekly summary's numbers from calls.json and compare.
Standard library only. Text-based checks are marked [HEURISTIC]."""
import json
import re
import sys
from pathlib import Path


def tools(call, name):
    return [t for t in call["tool_log"] if t["tool"] == name]


def ids(calls):
    return ", ".join(c["call_id"] for c in calls) or "-"


def reported(summary_text):
    """Read the outcome table out of the summary: '| Booked | 9 | 45% |'."""
    out = {}
    for label, n in re.findall(r"^\| ([A-Za-z ]+?) \| (\d+) \| \d+% \|$", summary_text, re.M):
        out[label] = int(n)
    return out


def main(calls_path="calls.json", summary_path="data/3-weekly-summary.md"):
    calls = json.loads(Path(calls_path).read_text(encoding="utf-8"))
    rep = reported(Path(summary_path).read_text(encoding="utf-8"))
    N = len(calls)
    rows = []  # (metric, reported, recomputed, call ids)

    def frac(n):
        return f"{n}/{N}"

    # outcome as the assistant logged it (log_outcome tool args)
    def logged(o):
        return [c for c in calls if any(t["args"].get("outcome") == o for t in tools(c, "log_outcome"))]

    # --- bookings
    lb = logged("booked")
    ok = [c for c in calls if any(t["result"].get("status") == "ok" for t in tools(c, "book_appointment"))]
    rows.append(("Booked: summary vs log_outcome=booked", frac(rep["Appointment booked"]), frac(len(lb)), ids(lb)))
    rows.append(("Booked: summary vs book_appointment status=ok", frac(rep["Appointment booked"]), frac(len(ok)), ids(ok)))
    unconf = [c for c in lb if c not in ok]
    rows.append(("Logged booked with no ok book_appointment", "not reported", f"{len(unconf)}/{len(lb)} logged-booked", ids(unconf)))
    attempted = [c for c in calls if tools(c, "book_appointment")]
    failed = [c for c in attempted if c not in ok]
    rows.append(("book_appointment attempted but errored", "not reported", f"{len(failed)}/{len(attempted)} attempts", ids(failed)))

    # --- transfers
    lt = logged("transferred")
    tattempt = [c for c in calls if tools(c, "transfer_to_advisor")]
    tconn = [c for c in tattempt if any(t["result"].get("status") == "connected" for t in tools(c, "transfer_to_advisor"))]
    tfail = [c for c in tattempt if c not in tconn]
    rows.append(("Transferred: summary vs log_outcome=transferred", frac(rep["Transferred to advisor"]), frac(len(lt)), ids(lt)))
    rows.append(("Transferred: summary vs transfer status=connected", frac(rep["Transferred to advisor"]), frac(len(tconn)), ids(tconn)))
    rows.append(("Transfer attempted but not connected", "not reported", f"{len(tfail)}/{len(tattempt)} attempts", ids(tfail)))

    # --- callbacks and no_action (same test: logged vs tool)
    lc = logged("callback")
    cb = [c for c in calls if any(t["result"].get("status") == "ok" for t in tools(c, "log_callback"))]
    rows.append(("Callback: summary vs log_outcome=callback", frac(rep["Callback requested"]), frac(len(lc)), ids(lc)))
    rows.append(("Callback: summary vs log_callback status=ok", frac(rep["Callback requested"]), frac(len(cb)), ids(cb)))
    ln = logged("no_action")
    rows.append(("No action: summary vs log_outcome=no_action", frac(rep["No action"]), frac(len(ln)), ids(ln)))

    # --- status calls (no summary category exists for these)
    gvs = [c for c in calls if tools(c, "get_vehicle_status")]
    rows.append(("get_vehicle_status called", "not reported", frac(len(gvs)), ids(gvs)))
    open_jc = [c for c in calls if any(t["result"].get("open_job_cards") for t in tools(c, "lookup_customer"))]
    rows.append(("Status: caller has open job card [proxy, structural]", "not reported", frac(len(open_jc)), ids(open_jc)))
    kw = re.compile(r"\b(ready|status|update|arrived|claim|waiting for the part|with you since|already with|at your workshop|inside your workshop|went in|gave my car)\b", re.I)
    s1 = [c for c in calls if any(kw.search(u["text"]) for u in c["transcript"] if u["speaker"] == "Caller")]
    rows.append(("Status: caller words match keywords [HEURISTIC]", "not reported", frac(len(s1)), ids(s1)))
    s3 = [c for c in calls if any(re.search(r"status", json.dumps(t["args"]), re.I)
                                  for t in tools(c, "transfer_to_advisor") + tools(c, "log_callback") + tools(c, "log_outcome"))]
    rows.append(("Status: assistant's own tool args say 'status' [HEURISTIC]", "not reported", frac(len(s3)), ids(s3)))
    sset = set(c["call_id"] for c in s1) | set(c["call_id"] for c in open_jc) | set(c["call_id"] for c in s3)
    sc = [c for c in calls if c["call_id"] in sset]
    rows.append(("Status calls, union of the three signals", "not reported", frac(len(sc)), ids(sc)))
    stat_booked = [c for c in sc if c in lb]
    rows.append(("  of those, logged booked", "not reported", f"{len(stat_booked)}/{len(sc)} status calls", ids(stat_booked)))
    stat_gvs = [c for c in sc if c in gvs]
    rows.append(("  of those, get_vehicle_status used", "not reported", f"{len(stat_gvs)}/{len(sc)} status calls", ids(stat_gvs)))

    # --- try to find another derivation that also gives the summary's 9
    cands = {
        "check_availability called": [c for c in calls if tools(c, "check_availability")],
        "check_availability returned >=1 slot": [c for c in calls if any(t["result"].get("slots") for t in tools(c, "check_availability"))],
        "book_appointment called": attempted,
        "lookup_customer found customer": [c for c in calls if any("customer_id" in t["result"] for t in tools(c, "lookup_customer"))],
    }
    for name, cs in cands.items():
        rows.append((f"Alt derivation of 9: {name}", frac(rep["Appointment booked"]), frac(len(cs)), ids(cs)))

    # --- average duration (excluding <15s per the summary's method note)
    d = [c["duration_sec"] for c in calls if c["duration_sec"] >= 15]
    avg = sum(d) / len(d)
    rows.append(("Avg duration, calls >=15s (summary: 2 min 53 sec)", "2:53", f"{int(avg // 60)}:{round(avg % 60):02d} over {len(d)}/{N} calls", "all"))

    # --- last week
    rows.append(("Last week figures (17 calls, 6 booked, 6 transfers)", "17/6/6", "no source in pack", "-"))

    w = max(len(r[0]) for r in rows)
    print(f"{'metric'.ljust(w)} | reported | recomputed | call IDs")
    print("-" * (w + 40))
    for m, r, c, i in rows:
        print(f"{m.ljust(w)} | {r:<8} | {c} | {i}")
    print("\nHEURISTIC rows use caller wording / tool-arg text and can miss or over-match.")
    contradictions(calls, "data/2-call-records.md")


# ---------------------------------------------------------------- per-call contradiction rules
RECORDS = "data/2-call-records.md"
TIME = re.compile(r"\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b", re.I)
RAW_CALL = re.compile(r"^(\d{2}:\d{2}:\d{2})\s+(\w+)\s")
RAW_HEAD = re.compile(r"^### (C-\d+) \|")


def raw_index(path):
    """Verbatim source lines: per call, tool blocks (in log order) and transcript turns, with line numbers."""
    idx, cur, fence = {}, None, False
    for n, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        m = RAW_HEAD.match(line)
        if m:
            cur = idx.setdefault(m.group(1), {"tools": [], "turns": []})
            continue
        if cur is None:
            continue
        if line.startswith("```"):
            fence = not fence
        elif fence and RAW_CALL.match(line):
            cur["tools"].append({"line": n, "text": [line.strip()]})
        elif fence and line.strip() and cur["tools"]:
            cur["tools"][-1]["text"].append(line.strip())
        elif line.startswith("> **"):
            cur["turns"].append({"line": n, "text": line[2:].strip()})
    return idx


def to24(h, mi, ap):
    h = int(h) % 12 + (12 if ap.lower() == "pm" else 0)
    return f"{h:02d}:{mi or '00'}"


def contradictions(calls, records_path):
    raw = raw_index(records_path)
    fired = {}  # call_id -> {rule: [evidence strings]}

    def ev_tool(cid, i):
        b = raw[cid]["tools"][i]
        return f"{records_path}:{b['line']}  " + "  ".join(b["text"])

    def ev_turn(cid, t):
        for r in raw[cid]["turns"]:
            if r["text"].endswith(t["text"]):
                return f"{records_path}:{r['line']}  {r['text']}"
        return t["text"]

    def fire(cid, rule, *evidence):
        fired.setdefault(cid, {}).setdefault(rule, []).extend(evidence)

    for c in calls:
        cid, log = c["call_id"], c["tool_log"]
        assert len(log) == len(raw[cid]["tools"]), cid
        idx = {k: [i for i, t in enumerate(log) if t["tool"] == k] for k in set(t["tool"] for t in log)}
        outcome_i = idx.get("log_outcome", [None])[-1]
        outcome = log[outcome_i]["args"].get("outcome") if outcome_i is not None else None
        book_i = idx.get("book_appointment", [])
        book_ok = [i for i in book_i if log[i]["result"].get("status") == "ok"]

        # R1: logged booked, no book_appointment returned ok
        if outcome == "booked" and not book_ok:
            e = [ev_tool(cid, outcome_i)]
            e += [ev_tool(cid, i) for i in book_i] or ["(no book_appointment call anywhere in this tool log)"]
            fire(cid, "R1", *e)

        # R2: any error return, then a later log_outcome=booked
        errs = [i for i, t in enumerate(log) if "error" in t["result"]]
        if outcome == "booked" and errs and errs[0] < outcome_i:
            fire(cid, "R2", *[ev_tool(cid, i) for i in errs if i < outcome_i], ev_tool(cid, outcome_i))

        # R3: transfer no_answer, no log_callback afterwards
        for i in idx.get("transfer_to_advisor", []):
            if log[i]["result"].get("status") == "no_answer" and not any(j > i for j in idx.get("log_callback", [])):
                fire(cid, "R3", ev_tool(cid, i), "(no log_callback call after this line)")

        # R4 [HEURISTIC]: time spoken in the last assistant turn naming a time vs confirmed_local
        for i in book_ok:
            conf = re.search(r"(\d{2}:\d{2}) IST", log[i]["result"].get("confirmed_local", ""))
            turns = [t for t in c["transcript"] if t["speaker"] == "Assistant" and TIME.search(t["text"])]
            if conf and turns:
                spoken = {to24(*m) for m in TIME.findall(turns[-1]["text"])}
                if conf.group(1) not in spoken:
                    slot = None
                    for j in idx.get("check_availability", []):
                        for sl in log[j]["result"].get("slots", []):
                            if sl["slot_id"] == log[i]["args"]["slot_id"]:
                                slot = (j, sl)
                    e = [ev_turn(cid, turns[-1]), ev_tool(cid, i)]
                    if slot:
                        e.append(ev_tool(cid, slot[0]))
                        utc = slot[1]["start"][11:16]
                        e.append(f"spoken {sorted(spoken)} vs slot start (UTC clock) {utc}: "
                                 f"{'equal' if utc in spoken else 'not equal'}; slot has start_local: {'start_local' in slot[1]}")
                    fire(cid, "R4", *e)

        # R5: open job card at lookup, no get_vehicle_status anywhere
        for i in idx.get("lookup_customer", []):
            if log[i]["result"].get("open_job_cards") and not idx.get("get_vehicle_status"):
                fire(cid, "R5", ev_tool(cid, i), "(no get_vehicle_status call in this tool log)")

    rules = ["R1", "R2", "R3", "R4", "R5"]
    print("\n\n== Contradictions inside a call (20 calls) ==")
    print("R1 booked logged, no ok book_appointment | R2 error return then booked logged | R3 transfer no_answer, no callback")
    print("R4 spoken time != confirmed_local [HEURISTIC, reads transcript text] | R5 open job card, no get_vehicle_status\n")
    print("call | logged outcome | R1 | R2 | R3 | R4 | R5 | rules fired")
    print("-----|----------------|----|----|----|----|----|------------")
    for c in calls:
        f = fired.get(c["call_id"], {})
        o = c["logged_outcome"]
        print(f"{c['call_id']} | {o:<22} | " + " | ".join(" X" if r in f else " ." for r in rules) + f" | {len(f)}")
    print("\nTotals (denominator 20 calls): " + ", ".join(
        f"{r} {sum(1 for f in fired.values() if r in f)}/20" for r in rules)
        + f"; calls with at least one: {len(fired)}/20; none: {20 - len(fired)}/20")
    print("\n== Evidence for every rule that fired ==")
    for c in calls:
        for r in rules:
            if r in fired.get(c["call_id"], {}):
                print(f"\n{c['call_id']} {r}" + ("  [HEURISTIC]" if r == "R4" else ""))
                for line in fired[c["call_id"]][r]:
                    print("  " + line)


if __name__ == "__main__":
    main(*sys.argv[1:3])
