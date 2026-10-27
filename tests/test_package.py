"""Package checks establish consistency, not agent effectiveness."""

import json
from pathlib import Path
import re
import unittest
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parents[1]


class PackageTests(unittest.TestCase):
    def test_skill_metadata_and_folder_match(self):
        skill = ROOT / "skills" / "feedback-to-fix" / "SKILL.md"
        text = skill.read_text(encoding="utf-8")
        frontmatter = text.split("---", 2)[1]
        self.assertRegex(frontmatter, r"(?m)^name: feedback-to-fix$")
        self.assertRegex(frontmatter, r"(?m)^description: .+Skip .+$")
        self.assertLess(len(text.split()), 1100)

    def test_relative_markdown_links_resolve_inside_package(self):
        for document in ROOT.rglob("*.md"):
            if ".git" in document.relative_to(ROOT).parts:
                continue
            for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", document.read_text(encoding="utf-8")):
                parsed = urlparse(target)
                if parsed.scheme or not parsed.path:
                    continue
                resolved = (document.parent / unquote(parsed.path)).resolve()
                with self.subTest(document=str(document.relative_to(ROOT)), link=target):
                    self.assertTrue(resolved.is_relative_to(ROOT))
                    self.assertTrue(resolved.exists())

    def test_suite_has_controls_and_no_shipped_behavioral_results(self):
        suite = json.loads((ROOT / "evals" / "cases.json").read_text(encoding="utf-8"))
        self.assertEqual(len(suite["cases"]), 8)
        self.assertEqual(sum(case["control"] for case in suite["cases"]), 2)
        template = json.loads((ROOT / "evals" / "scores.template.json").read_text(encoding="utf-8"))
        self.assertEqual(template["runs"], [])


if __name__ == "__main__":
    unittest.main()
