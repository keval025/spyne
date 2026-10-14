Fix: one prompt rule, edited tonight. Assumption: I can edit the prompt but not the tools.

Add: "Before log_outcome with outcome booked, confirm book_appointment returned status ok in this call. If it did not, never log booked. Log callback if the caller asked for one, transferred if connected, otherwise no_action, and put what happened in the notes."

Check tomorrow: export the day's calls in the same format and run audit.py. Pass: rule R1 (booked logged, no ok book_appointment) fires on 0 of the day's calls; last week it fired on 5 of 20. Inconclusive if no call that day reached a failed or missing booking, so extend a day. I also read the day's non-booked outcomes by hand.

Not covered: wrong spoken times and status calls (see ticket).
