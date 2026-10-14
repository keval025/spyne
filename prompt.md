# Session log: prompt history

Sparsh Motors Kothrud call audit. One working session, in order. User prompts are quoted
verbatim (the long first prompt is trimmed to its instructions). Each entry says what was done
and what was checked. Nothing here counts towards the 800-word limit.

## 1. Read the pack, no analysis

> Role: You are a forward-deployed engineer on a night shift.
> Context: data/ has a brief, 20 call records with tool logs, a weekly summary and a tool reference for a Pune car workshop's AI phone assistant.
> Task: Read all four files. Then give me: (1) what the brief asks me to deliver, with limits, (2) three questions the pack leaves unanswered, (3) a proposed repo layout. Do not analyse the calls yet.
> Constraints: No code. Quote the brief for every limit.

(Five files attached: the four markdown files and a "read me first" docx.)

- Read all five. Checked the docx against the markdown files: same content, only list numbering differs.
- Found the repo empty (no commits, no `data/`). Flagged it.
- Output: deliverables a to g with quoted limits, the 800-word budget arithmetic, three open questions (what can be changed tonight; any ground truth beyond the assistant's own logs; what "good" means and who acts on callbacks), and a repo layout.

## 2. Repo URL

> https://github.com/keval025/spyne.git

- Confirmed it is already `origin`. Fetched: remote has no branches. Asked before scaffolding.

## 3. Parser

> Task: Write parse.py (standard library only) that turns data/2-call-records.md into calls.json: one object per call with transcript turns, logged outcome, duration, and the tool log as a list of {tool, args, result}.
> Constraints: Handle multi-line results. Add a test that checks 20 calls and 4 book_appointment calls with status ok. If the test fails, show me the failure.

- Wrote `parse.py` and `tests/test_parse.py`. Added a third test for a multi-line result (C-01 `check_availability`).
- Test result: 3 of 3 pass. 20 calls, 4 ok bookings (C-01, C-08, C-09, C-18). No failure to show.
- First commit and push attempt was blocked by the permission classifier. I did not work around it and asked how to proceed.

## 4. Hypothesis test

> Hypothesis: The weekly summary is built from the assistant's own log_outcome, not from what the tools confirmed.
> Task: Try to prove me wrong. Write audit.py that recomputes bookings, transfers and status calls from calls.json and prints a table of reported vs recomputed numbers.
> Constraints: Every number gets a denominator and call IDs. Mark any text-based check as a heuristic.

- Wrote `audit.py`. Result: summary equals `log_outcome` on all four outcome counts (9, 5, 2, 4 of 20). Tool-confirmed bookings are 4 of 20.
- Tried four alternative derivations of the summary's 9 (availability called, slots returned, customer found, booking called). None gives 9.
- Could not separate the sources for transfers, callbacks or no-action, because both agree. Said so.
- Disclosed that the status keyword list was written after reading the calls, so it is partly fitted to the data.

## 5. Contradiction rules

> Task: Extend audit.py with rules for contradictions inside a call: a booking without an ok result, an error return followed by a success log, a no_answer transfer without a callback, a spoken time that differs from confirmed_local, an open job card with no status lookup. Output a 20-row exhibit table.
> Constraints: Show me any rule that fires and the evidence line from the tool log.

- Added rules R1 to R5 and the 20-row exhibit with verbatim source lines (`data/2-call-records.md:<line>`).
- Results over 20 calls: R1 5, R2 3, R3 1, R4 2, R5 8; 14 calls fire at least one rule.
- Flagged that R2 also fires on a lookup `NOT_FOUND` followed by a booking, which may be legitimate. Only C-13's error is a booking error. R4 is marked heuristic.

## 6. Choosing a call to trace

> Task: Propose three calls that would make a good end-to-end trace and rank them by how clearly one tool call is the point of failure. Then trace the top one, naming the exact call and why it went wrong.
> Constraints: Cite log timestamps. Say what you cannot tell from the log.

- Ranked C-13, C-09, C-02. Traced C-13: `book_appointment` with slot_id `S-SUN-0900` at 10:12:20 returned `WORKSHOP_CLOSED`; `log_outcome` booked at 10:12:29.
- **Correction of my own earlier claim:** I had suggested the spoken times in C-08 and C-09 were UTC read as local time. In C-09 the same turn offered "Friday at 4 pm", which matches S-4444 (10:30Z = 16:00 IST). So one slot was converted correctly and the other was not. I withdrew the UTC explanation.

## 7. Draft sections a to e

> Task: Draft sections a to e: facts (<250 words), trace, manager note (<80 words), a ten-line engineering ticket, and one fix I can ship tonight with a check for tomorrow.
> Constraints: The manager note promises nothing we cannot keep. Total 800 words. Write wordcount.py to check each limit.

- Wrote `deliverables/a` to `e` and `wordcount.py`.
- Result: a 216, b 150, c 61, d 153 (10 lines), e 128. Total 708 of 800, leaving 92 for f.
- Fix chosen: one prompt rule (never log booked unless `book_appointment` returned ok in that call). Check: R1 fires on 0 of the day's calls, against 5 of 20 last week.

## 8. Strict review

> Role: Act as a strict reviewer of my draft.
> Task: Check every number against calls.json, recount it independently, and list each violation of the brief with its location. Also list anything the AI told me that I should verify by hand against a transcript.
> Constraints: Do not fix anything yet. Report only.

- Recounted with fresh code (not `audit.py`) and cross-checked the raw file. Every number reproduced.
- Listed ten brief violations. Main ones:
  - c: "Five callers" has no denominator.
  - a: "up 50%" and "6 bookings" have no denominator.
  - a: the "Only 2 of 20" sentence relies on the heuristic but is not marked.
  - d: a dev who has never seen the pack cannot act on it cold.
  - Assumptions are not collected in one place.
- Accuracy problems: c says "have no appointment" where the log shows only no confirmed booking; b states "the summary counts this entry" as fact while a calls it an assumption.
- Hand-verification list for transcripts: the 8 status calls (especially C-17, an insurance claim), C-08 and C-09 spoken times, C-13 agreement, C-01 and C-18 matches, the "Friday 4 pm" arithmetic.

## 9. PDF, README, secrets check

> Task: After I fix the review items, build a PDF of the answer with the exhibit table, write a README with run commands, and check that the repo contains no secrets.
> Constraints: Report the final word count. Do not push until I say so.

- Checked first: the drafts had not changed since the review, so the review fixes were not in. I did not produce a final PDF or final word count.
- Did the parts that do not depend on the fixes: secrets scan (clean, one false positive on the word "tokens"), `README.md`, `.gitignore`, and `build_pdf.py` (test build to the scratchpad, 20 exhibit rows).

## 10. Commit and push, in steps

> commit all the code

- Committed the six code files only (`3a914b5`), not pushed.

> push all code

- Pushed. Verified the remote branch matches local `HEAD`.

> commit and push them now

- Re-ran the secrets scan (clean), committed the README, `calls.json`, `data/` and `deliverables/` (`add400c`), pushed, and verified the remote.

## 11. This file

> give me prompt.md file of this session

## Notes

- The stop hook repeatedly asked to commit and push untracked files. I did not treat it as permission to override your instruction not to push, or the earlier classifier block. I asked each time and acted only on your explicit instructions.
- Where I pushed back on myself: the UTC explanation (withdrawn), the tuned keyword list (disclosed), the R2 over-firing (flagged), and the "have no appointment" overclaim in c (found in review).

## Open at time of writing

- The review fixes are not yet applied to `deliverables/`.
- Section f (two AI answers not taken) and the final `answer.pdf` are not written.
- Final word count is pending. Current a to e total is 708 of 800.
