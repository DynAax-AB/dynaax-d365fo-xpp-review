"""Checks that every skill in skills/ is well formed, that the review rules
follow the rule format, and that the samples point at real rules.

Run from the repository folder:

    python3 tests/check_skills.py            # offline checks
    python3 tests/check_skills.py --online   # also checks every link opens

Needs only Python 3.9 or later, no extra packages.
"""

import re
import sys
import unittest
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
ONLINE = "--online" in sys.argv
OWN_REPO_URL = "https://github.com/DynAax-AB/dynaax-d365fo-xpp-review"
RULES = SKILLS / "xpp-code-review" / "references" / "rules.md"
SAMPLES = ROOT / "samples"
EXPECTED = SAMPLES / "expected-findings.md"

REQUIRED_SECTIONS = [
    "## When to use this skill",
    "## Ask these first",
    "## How to work through it",
    "## How to answer",
    "## When to hand over to a person",
    "## Ground rules",
    "## Further reading (Microsoft Learn)",
]
NAME_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
LINK_PATTERN = re.compile(r"\[[^\]]*\]\((https?://[^)\s]+)\)")
ALLOWED_LINK_HOST = "https://learn.microsoft.com/"
SEVERITIES = {"Blocker", "Major", "Minor", "Question"}
RULE_HEADING = re.compile(r"^### ([A-Z]{2,3}-\d{2}) (.+)$", re.M)
RULE_ID = re.compile(r"\b[A-Z]{2,3}-\d{2}\b")
RULE_PARTS = ["**Severity:**", "**Look for:**", "**Why it matters:**", "**Fix:**"]
VERDICTS = {"Ready to merge", "Merge after small fixes", "Needs changes before merge"}


def skill_dirs():
    return sorted(p for p in SKILLS.iterdir() if p.is_dir())


def parse_frontmatter(text):
    """Reads the simple YAML used in SKILL.md: top-level keys plus one nested map."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("SKILL.md must start with a '---' frontmatter line")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError("frontmatter has no closing '---' line") from exc

    data, current_map = {}, None
    for line in lines[1:end]:
        if not line.strip():
            continue
        key, _, value = line.strip().partition(":")
        value = value.strip().strip('"')
        if line.startswith((" ", "\t")):
            if current_map is None:
                raise ValueError(f"indented line outside a map: {line!r}")
            current_map[key] = value
        elif value:
            data[key], current_map = value, None
        else:
            current_map = data[key] = {}
    return data, "\n".join(lines[end + 1 :])


def links_in(path):
    return LINK_PATTERN.findall(path.read_text(encoding="utf-8"))


class SkillChecks(unittest.TestCase):
    def test_there_are_skills(self):
        self.assertTrue(skill_dirs(), "no skill folders found under skills/")

    def test_frontmatter(self):
        for folder in skill_dirs():
            with self.subTest(skill=folder.name):
                meta, _ = parse_frontmatter((folder / "SKILL.md").read_text(encoding="utf-8"))
                name = meta.get("name", "")
                self.assertEqual(name, folder.name, "name must match the folder name")
                self.assertRegex(name, NAME_PATTERN)
                self.assertLessEqual(len(name), 64)

                description = meta.get("description", "")
                self.assertTrue(description, "description is missing")
                self.assertLessEqual(len(description), 1024, "description is too long")
                self.assertNotRegex(description, r"[<>]", "description must not contain < or >")

                self.assertEqual(meta.get("license"), "MIT")
                extra = meta.get("metadata", {})
                self.assertIsInstance(extra, dict, "metadata must be a map")
                status = extra.get("status", "")
                self.assertTrue(
                    status.startswith("draft") or status == "reviewed",
                    f"status must start with 'draft' or be 'reviewed', got {status!r}",
                )
                self.assertTrue(extra.get("checked-against"), "checked-against is missing")

    def test_body(self):
        for folder in skill_dirs():
            with self.subTest(skill=folder.name):
                text = (folder / "SKILL.md").read_text(encoding="utf-8")
                meta, body = parse_frontmatter(text)
                for heading in REQUIRED_SECTIONS:
                    self.assertIn(heading, body, f"missing section {heading!r}")
                self.assertLess(len(text.splitlines()), 500, "keep SKILL.md under 500 lines")
                if meta["metadata"]["status"].startswith("draft"):
                    self.assertIn("**Draft: Nurlin to review.**", body, "draft banner missing")

    def test_referenced_files_exist(self):
        for folder in skill_dirs():
            with self.subTest(skill=folder.name):
                text = (folder / "SKILL.md").read_text(encoding="utf-8")
                for ref in re.findall(r"`(references/[\w./-]+)`", text):
                    self.assertTrue((folder / ref).is_file(), f"{ref} is mentioned but missing")

    def test_test_questions(self):
        for folder in skill_dirs():
            with self.subTest(skill=folder.name):
                path = folder / "test-questions.md"
                self.assertTrue(path.is_file(), "test-questions.md is missing")
                questions = re.split(r"^### ", path.read_text(encoding="utf-8"), flags=re.M)[1:]
                self.assertTrue(3 <= len(questions) <= 5, f"need 3-5 questions, found {len(questions)}")
                for question in questions:
                    self.assertIn("Must cover:", question, f"no 'Must cover:' under {question.splitlines()[0]!r}")

    def test_skill_links_point_to_learn(self):
        for path in SKILLS.rglob("*.md"):
            for url in links_in(path):
                with self.subTest(file=str(path.relative_to(ROOT)), url=url):
                    self.assertTrue(url.startswith(ALLOWED_LINK_HOST), "skills link only to Microsoft Learn")
                    self.assertNotIn("?", url, "drop tracking or context parameters from links")

    @unittest.skipUnless(ONLINE, "run with --online to check links")
    def test_links_open(self):
        urls = sorted({u for p in ROOT.rglob("*.md") if ".git" not in p.parts for u in links_in(p)})
        urls = [u for u in urls if "..." not in u and "<" not in u]
        # Links to this repo's own GitHub pages (badges, Actions) only open
        # once the repo is public, so they're left out.
        urls = [u for u in urls if not u.startswith(OWN_REPO_URL)]
        for url in urls:
            with self.subTest(url=url):
                request = urllib.request.Request(url, headers={"User-Agent": "skill-link-check"})
                try:
                    with urllib.request.urlopen(request, timeout=20) as response:
                        self.assertEqual(response.status, 200)
                except urllib.error.HTTPError as err:
                    self.fail(f"HTTP {err.code}")


def rules():
    """Returns {rule ID: rule text} from rules.md."""
    text = RULES.read_text(encoding="utf-8")
    found, matches = {}, list(RULE_HEADING.finditer(text))
    for i, match in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[match.end() : end].split("\n## ", 1)[0]
        if match.group(1) in found:
            raise ValueError(f"rule {match.group(1)} appears twice")
        found[match.group(1)] = body
    return found


def expected_sections():
    """Returns {sample file name: section text} from expected-findings.md."""
    parts = re.split(r"^## ", EXPECTED.read_text(encoding="utf-8"), flags=re.M)[1:]
    return {p.splitlines()[0].strip(): p for p in parts}


class RuleChecks(unittest.TestCase):
    def test_rules_have_every_part(self):
        found = rules()
        self.assertGreaterEqual(len(found), 40, "expected the full rule list")
        for rule_id, body in found.items():
            with self.subTest(rule=rule_id):
                for part in RULE_PARTS:
                    self.assertIn(part, body, f"{part} missing")
                severity = re.search(r"\*\*Severity:\*\* (\w+)", body).group(1)
                self.assertIn(severity, SEVERITIES)

    def test_every_area_has_a_learn_source(self):
        text = RULES.read_text(encoding="utf-8")
        for area in re.split(r"^## ", text, flags=re.M)[1:]:
            with self.subTest(area=area.splitlines()[0]):
                self.assertRegex(area, r"Source: \[[^\]]+\]\(https://learn\.microsoft\.com/")

    def test_skill_table_matches_rules(self):
        skill = (SKILLS / "xpp-code-review" / "SKILL.md").read_text(encoding="utf-8")
        prefixes = {r.split("-")[0] for r in rules()}
        for prefix in prefixes:
            with self.subTest(area=prefix):
                last = max(r for r in rules() if r.startswith(prefix + "-"))
                self.assertIn(f"{prefix}-01 to {last}", skill, "rule area table in SKILL.md is out of date")

    def test_rule_ids_in_skill_files_exist(self):
        known = set(rules())
        for path in list((SKILLS / "xpp-code-review").rglob("*.md")) + [EXPECTED]:
            for rule_id in RULE_ID.findall(path.read_text(encoding="utf-8")):
                with self.subTest(file=str(path.relative_to(ROOT)), rule=rule_id):
                    self.assertIn(rule_id, known)


class SampleChecks(unittest.TestCase):
    def test_every_sample_is_a_diff_with_expectations(self):
        sections = expected_sections()
        diffs = sorted(SAMPLES.glob("*.diff"))
        self.assertTrue(diffs, "no sample diffs found")
        self.assertEqual(sorted(sections), [d.name for d in diffs], "samples and expected-findings.md differ")
        for diff in diffs:
            with self.subTest(sample=diff.name):
                self.assertTrue(diff.read_text(encoding="utf-8").startswith("diff --git "))

    def test_expectations_are_complete(self):
        for name, section in expected_sections().items():
            with self.subTest(sample=name):
                verdict = re.search(r"\*\*Verdict:\*\* (.+)", section).group(1).strip()
                allowed = [v.strip() for v in verdict.split(", or ")]
                for v in allowed:
                    self.assertIn(v, VERDICTS)
                must = re.search(r"\*\*Must find:\*\* (.+)", section).group(1)
                if name.startswith("good-"):
                    self.assertNotIn("Needs changes before merge", allowed)
                    self.assertTrue(must.startswith("none"), "good samples must expect no Blocker or Major")
                else:
                    self.assertEqual(allowed, ["Needs changes before merge"])
                    self.assertTrue(RULE_ID.findall(must), "bad samples must list the rules they break")


def report_review_markers():
    markers = []
    for path in sorted(ROOT.rglob("*.md")):
        if ".git" in path.parts:
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if "REVIEW:" in line and "<!--" in line:
                markers.append(f"  {path.relative_to(ROOT)}:{number}")
    if markers:
        print(f"\n{len(markers)} REVIEW notes still open:")
        print("\n".join(markers))


if __name__ == "__main__":
    argv = [a for a in sys.argv if a != "--online"]
    result = unittest.main(argv=argv, exit=False, verbosity=2).result
    report_review_markers()
    sys.exit(0 if result.wasSuccessful() else 1)
