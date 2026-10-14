import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import parse  # noqa: E402


class ParseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.calls = parse.parse((ROOT / "data" / "2-call-records.md").read_text(encoding="utf-8"))

    def test_twenty_calls(self):
        self.assertEqual(len(self.calls), 20)

    def test_four_book_appointment_ok(self):
        ok = [
            c["call_id"]
            for c in self.calls
            for t in c["tool_log"]
            if t["tool"] == "book_appointment" and t["result"].get("status") == "ok"
        ]
        self.assertEqual(len(ok), 4, ok)

    def test_multiline_result(self):
        # C-01 check_availability result spans two lines in the source
        t = self.calls[0]["tool_log"][1]
        self.assertEqual(t["tool"], "check_availability")
        self.assertEqual(len(t["result"]["slots"]), 2)


if __name__ == "__main__":
    unittest.main()
