import re
import unittest

from _contracts import REPO_ROOT

SKIP_DIRS = {".git", ".venv", "node_modules", "__pycache__", ".Rproj.user"}
FENCE = re.compile(r"^(```|~~~).*?^\1", re.S | re.M)
LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")


def _markdown_files():
    for path in REPO_ROOT.rglob("*.md"):
        if not SKIP_DIRS & set(path.relative_to(REPO_ROOT).parts):
            yield path


def _slug(heading: str) -> str:
    text = re.sub(r"[`*_]", "", heading.strip().lower())
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def _anchors(path) -> set[str]:
    body = FENCE.sub("", path.read_text(encoding="utf-8"))
    return {_slug(m.group(1)) for m in re.finditer(r"^#{1,6}\s+(.+?)\s*#*\s*$", body, re.M)}


class DocsLinkTests(unittest.TestCase):
    def test_every_internal_markdown_link_resolves(self) -> None:
        files = list(_markdown_files())
        self.assertGreater(len(files), 10)
        broken = []
        for path in files:
            body = FENCE.sub("", path.read_text(encoding="utf-8"))
            for match in LINK.finditer(body):
                target = match.group(1)
                if re.match(r"^(https?:|mailto:)", target):
                    continue
                file_part, _, anchor = target.partition("#")
                resolved = path if not file_part else (path.parent / file_part).resolve()
                rel = path.relative_to(REPO_ROOT)
                if not resolved.exists():
                    broken.append(f"{rel}: {target}")
                elif anchor and resolved.suffix == ".md" and _slug(anchor) not in _anchors(resolved):
                    broken.append(f"{rel}: {target} (missing anchor)")
        self.assertEqual(broken, [])

    def test_the_previously_missing_documents_exist_and_are_not_stubs(self) -> None:
        for relative in (
            "docs/reference-use-policy.md",
            "docs/templates/SKILL.template.md",
            "docs/development/positron-agent-workflow.md",
        ):
            with self.subTest(document=relative):
                text = (REPO_ROOT / relative).read_text(encoding="utf-8")
                self.assertGreater(len(text.splitlines()), 25)


if __name__ == "__main__":
    unittest.main()
