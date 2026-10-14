The weekly summary reports 9 of 20 calls as booked (45%). That equals the assistant's own log_outcome tally: 9 of 20 logged "booked" (C-01, C-02, C-03, C-05, C-08, C-09, C-10, C-13, C-18). The summary says its figures are "generated from assistant call logs".

The tools confirm only 4 of 20 (C-01, C-08, C-09, C-18): book_appointment returned status ok. The other 5 of the 9 logged bookings have no ok result. C-02, C-03, C-05 and C-10 made no booking call; C-13's returned WORKSHOP_CLOSED.

Of the 4 confirmed, 2 were told a different time from confirmed_local: C-08 said 10 am, confirmed 15:30 IST; C-09 said 9:30 am, confirmed 15:00 IST (transcript wording, heuristic). Only 2 of 20 calls (C-01, C-18) show a confirmed booking with a matching spoken time.

8 of 20 callers had an open job card at lookup (C-02, C-04, C-07, C-11, C-14, C-16, C-17, C-20); caller wording matched the same 8 (heuristic). get_vehicle_status was called in 0 of those 8. Only 3 of 8 reached an advisor (C-04, C-16, C-20). C-02's transfer returned no_answer, no callback followed, and it was logged "booked".

No source in the pack: last week's 17 calls and 6 bookings, so "up 50%" cannot be checked.

Assumption: the summary is built from log_outcome. I cannot see how the report is generated.
