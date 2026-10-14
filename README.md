# Sparsh Motors Kothrud: call audit

FDE case study. One week (18-23 Aug), 20 calls, one workshop. The pack is synthetic.

## Layout

- `data/` the pack files used by the scripts (`2-call-records.md`, `3-weekly-summary.md`)
- `parse.py` turns the call records into `calls.json` (standard library only)
- `audit.py` recomputes the summary's numbers and runs five contradiction rules per call
- `tests/test_parse.py` checks 20 calls and 4 `book_appointment` calls with status ok
- `deliverables/` sections a to f of the answer, one file each
- `wordcount.py` checks the brief's limits
- `build_pdf.py` builds `answer.pdf` (needs `pip install reportlab`)

## Run

```
python3 -I parse.py                       # writes calls.json
python3 -I -m unittest discover -s tests -v
python3 -I audit.py                       # reported vs recomputed, then the 20-row exhibit and evidence lines
python3 -I wordcount.py                   # exits 1 if a limit is broken
python3 build_pdf.py                      # writes answer.pdf
```

Run from the repo root. `audit.py` reads `calls.json` and `data/`, so run `parse.py` first.

## Limits checked by wordcount.py

a under 250 words, c under 80 words, d exactly ten lines, a to f together at most 800 words.
Words are whitespace-separated tokens containing a letter or digit. The exhibit is not counted.

## Notes

- Text-based checks are heuristics and are labelled as such in the output.
- Section g (session log) is not in this repo yet.
