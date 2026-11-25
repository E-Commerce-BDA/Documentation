"""Acceptance test for the ratchet: additions fail, removals never do."""

from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

import count_comments


class RatchetTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.repo = self.root / "demo-svc"
        (self.repo / "src").mkdir(parents=True)
        (self.repo / "dist").mkdir()
        self.baseline = self.root / "baseline.json"
        self.source = self.repo / "src" / "a.ts"

        # One reviewable comment, one sanctioned reason, a URL inside a string,
        # and a generated file that must not be counted.
        self.source.write_text(
            "// a plain helper note\n"
            "// reason: the fallback hides a parser bug, keep the note\n"
            'const url = "https://example.com//not-a-comment";\n'
            "const value = input ?? 0;\n",
            encoding="utf-8",
        )
        (self.repo / "dist" / "bundle.js").write_text(
            "// generated banner\nconst a = 1;\n", encoding="utf-8"
        )

        self.original_repos = count_comments.REPOS
        count_comments.REPOS = {"demo-svc": "demo-svc"}
        self.addCleanup(self._restore_repos)

    def _restore_repos(self) -> None:
        count_comments.REPOS = self.original_repos

    def run_main(self, *extra: str) -> int:
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
            code = count_comments.main(
                ["--root", str(self.root), "--baseline", str(self.baseline), *extra]
            )
        self.output = buffer.getvalue()
        return code

    def test_generated_and_sanctioned_comments_are_excluded(self) -> None:
        self.assertEqual(count_comments.count_repo(self.root, "demo-svc"), 1)

    def test_baseline_records_current_count(self) -> None:
        self.assertEqual(self.run_main("--update-baseline"), 0)
        payload = json.loads(self.baseline.read_text(encoding="utf-8"))
        self.assertEqual(payload["repos"], {"demo-svc": 1})

    def test_adding_one_unapproved_comment_fails(self) -> None:
        self.assertEqual(self.run_main("--update-baseline"), 0)
        with self.source.open("a", encoding="utf-8") as handle:
            handle.write("// one new unapproved note\n")
        self.assertEqual(self.run_main(), 1)
        self.assertIn("FAIL demo-svc: 2 reviewable comments > baseline 1", self.output)

    def test_removing_comments_never_fails(self) -> None:
        self.assertEqual(self.run_main("--update-baseline"), 0)
        self.source.write_text(
            'const url = "https://example.com//not-a-comment";\n'
            "const value = input ?? 0;\n",
            encoding="utf-8",
        )
        self.assertEqual(self.run_main(), 0)


if __name__ == "__main__":
    unittest.main()
