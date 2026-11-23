import re
import unittest

from _contracts import REPO_ROOT

LIFECYCLE = ["Inspect", "Profile", "Validate", "Diagnose", "Propose", "Approve", "Transform", "Verify", "Document"]
LIFECYCLE_LINE = " → ".join(LIFECYCLE)
SKILL_DIR = REPO_ROOT / "skills" / "statistical-data-manager"


class LifecycleConsistencyTests(unittest.TestCase):
    def test_readme_states_the_nine_step_lifecycle(self) -> None:
        self.assertIn(f"**{LIFECYCLE_LINE}**", (REPO_ROOT / "README.md").read_text(encoding="utf-8"))

    def test_architecture_doc_states_the_lifecycle(self) -> None:
        text = (REPO_ROOT / "docs/architecture/statistical-data-manager.md").read_text(encoding="utf-8")
        self.assertIn(" ".join(LIFECYCLE_LINE.split()), " ".join(text.replace("\n", " ").replace("**", "").split()))

    def test_protocol_lists_the_steps_in_order(self) -> None:
        text = (SKILL_DIR / "spec" / "protocol.md").read_text(encoding="utf-8")
        section = text.split("## Lifecycle", 1)[1].split("##", 1)[0]
        self.assertEqual(re.findall(r"^\d+\. \*\*(\w+)\*\*", section, re.M), LIFECYCLE)

    def test_skill_md_includes_an_approval_step_before_applying(self) -> None:
        text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertLess(text.index("approval, rejection, or deferral"), text.index("Apply only approved"))

    def test_the_old_eight_step_lifecycle_is_gone(self) -> None:
        old = "Propose → Transform"
        for path in REPO_ROOT.rglob("*.md"):
            if {".venv", ".git"} & set(path.relative_to(REPO_ROOT).parts):
                continue
            with self.subTest(document=str(path.relative_to(REPO_ROOT))):
                self.assertNotIn(old, path.read_text(encoding="utf-8"))


class DecisionRecordTests(unittest.TestCase):
    def test_adr_0002_is_proposed_and_open_items_are_registered(self) -> None:
        adr = (REPO_ROOT / "docs/decisions/0002-routing-provenance-and-state-model.md").read_text(encoding="utf-8")
        self.assertIn("**Status:** Proposed", adr)
        for topic in (
            "Deterministic engine routing", "No silent engine fallback", "Engine and capability provenance",
            "Coordination modes", "Disagreement preservation and reconciliation", "Release blockers", "State model",
        ):
            self.assertIn(topic, adr)
        register = (REPO_ROOT / "docs/decisions/open-decisions.md").read_text(encoding="utf-8")
        self.assertIn("schema `$id` base", register)
        self.assertIn("DESCRIPTION", register)

    def test_contact_address_is_not_copied_into_documentation(self) -> None:
        description = (SKILL_DIR / "r" / "DESCRIPTION").read_text(encoding="utf-8")
        address = re.search(r"email\s*=\s*\"([^\"]+)\"", description).group(1)
        for path in list((REPO_ROOT / "docs").rglob("*.md")) + list((REPO_ROOT / "schemas").rglob("*")):
            if path.is_file():
                with self.subTest(file=str(path.relative_to(REPO_ROOT))):
                    self.assertNotIn(address, path.read_text(encoding="utf-8"))

    def test_schema_id_base_is_unchanged_in_v01(self) -> None:
        for name in ("finding", "approval", "run-manifest"):
            text = (REPO_ROOT / "schemas" / f"{name}.schema.json").read_text(encoding="utf-8")
            self.assertIn(f"https://amphibiousintellect.org/suai/{name}.schema.json", text)


if __name__ == "__main__":
    unittest.main()
