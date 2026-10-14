import unittest, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from urag import pipeline, evaluate


class Cases(unittest.TestCase):
    corpus = pipeline.load(ROOT / "data/corpus.json")
    cases = pipeline.load(ROOT / "data/cases.json")

    def test_all_cases(self):
        for c in self.cases:
            with self.subTest(c["id"]):
                out = pipeline.investigate(self.corpus, c["user"], c["incident"])
                self.assertEqual(evaluate.check(c, out, self.corpus), [])

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
