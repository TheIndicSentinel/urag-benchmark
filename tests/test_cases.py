import unittest, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from urag import pipeline, evaluate


class Cases(unittest.TestCase):
    corpus = pipeline.load(ROOT / "data/corpus.json")
    cases = pipeline.load(ROOT / "data/cases.json")

    # Held-out failures documented in docs/RESULTS.md. Not fixed to avoid tuning
    # on held-out data; this test flips when the failure is resolved so it can't rot.
    KNOWN_FAILING = {"C8-dirty-service-env-metadata"}

    def test_all_cases(self):
        for c in self.cases:
            with self.subTest(c["id"]):
                out = pipeline.investigate(self.corpus, c["user"], c["incident"])
                fails = evaluate.check(c, out, self.corpus)
                if c["id"] in self.KNOWN_FAILING:
                    self.assertTrue(fails, "known failure now passes: update KNOWN_FAILING and RESULTS.md")
                else:
                    self.assertEqual(fails, [])

    def test_fail_closed_no_groups(self):
        out = pipeline.investigate(self.corpus, {"id": "x", "groups": []}, self.cases[0]["incident"])
        self.assertIsNone(out["applicable_runbook"])
        self.assertEqual(out["status"], "insufficient_evidence")

    def test_security_user_sees_security_runbook(self):
        # authorization is group-based, not role-name-based
        out = pipeline.investigate(self.corpus, {"id": "s", "groups": ["security-team"]}, self.cases[1]["incident"])
        self.assertEqual(out["applicable_runbook"]["id"], "rb-pay-sec")


if __name__ == "__main__":
    unittest.main()
