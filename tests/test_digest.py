import json, os, sys, tempfile, unittest, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from urag import public_eval as pe


class Digest(unittest.TestCase):
    def _tree(self, d, cases="a"):
        for rel, body in {"src/urag/pipeline.py": "p", "src/urag/public_eval.py": "e", "src/urag/gen/docs_gen.py": "g",
                          "configs/generator.json": "{}", "data/public/S1_cases.json": cases}.items():
            p = pathlib.Path(d, rel); p.parent.mkdir(parents=True, exist_ok=True); p.write_text(body)

    def test_digest_tracks_cases_and_config_not_docs(self):
        with tempfile.TemporaryDirectory() as d1, tempfile.TemporaryDirectory() as d2:
            self._tree(d1); self._tree(d2)
            a = pe.pipeline_digest(pe.pipeline_manifest(d1))
            self.assertEqual(a, pe.pipeline_digest(pe.pipeline_manifest(d2)))
            pathlib.Path(d1, "docs").mkdir(); pathlib.Path(d1, "docs/PREREGISTRATION.md").write_text("amended")
            self.assertEqual(a, pe.pipeline_digest(pe.pipeline_manifest(d1)))  # docs excluded
            pathlib.Path(d2, "data/public/S1_cases.json").write_text("b")
            self.assertNotEqual(a, pe.pipeline_digest(pe.pipeline_manifest(d2)))  # cases included
            pathlib.Path(d1, "configs/generator.json").write_text('{"x":1}')
            self.assertNotEqual(a, pe.pipeline_digest(pe.pipeline_manifest(d1)))  # config included


if __name__ == "__main__":
    unittest.main()
