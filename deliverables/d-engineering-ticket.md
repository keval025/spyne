Bug: assistant logs "booked" with no confirmed booking and tells callers wrong times (KTD-04, 18-23 Aug).
Evidence: 9 of 20 calls logged booked; only 4 of 20 had book_appointment status ok. No ok result: C-02, C-03, C-05, C-10, C-13.
C-13: book_appointment S-SUN-0900 (10:12:20) returned WORKSHOP_CLOSED; log_outcome booked followed (10:12:29).
Wrong time: diagnostic and inspection slots carry no start_local. C-08 and C-09 were told 10 am and 9:30 am; confirmed_local was 15:30 and 15:00 IST.
Status: 8 of 20 callers had an open job card; get_vehicle_status was called in 0 of 8.
C-02: transfer returned no_answer (11:17:02), no log_callback, then logged booked.
Expected per tool reference: booked only after status ok; errors are failures; no_answer needs a callback.
Ask 1: reject log_outcome booked unless book_appointment returned ok in the same call.
Ask 2: return start_local on every slot; reject slot_ids that check_availability did not return.
Unknown: is get_vehicle_status enabled? Repro calls: C-13, C-02, C-08.
