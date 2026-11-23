import shutil
import subprocess
import unittest

from _contracts import REPO_ROOT


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=REPO_ROOT, capture_output=True, text=True)


@unittest.skipUnless(shutil.which("git") and (REPO_ROOT / ".git").exists(), "requires a git checkout")
class RepoHygieneTests(unittest.TestCase):
    def test_no_bytecode_or_cache_directories_are_tracked(self) -> None:
        tracked = _git("ls-files").stdout.splitlines()
        offenders = [p for p in tracked if p.endswith((".pyc", ".pyo")) or "__pycache__/" in p]
        self.assertEqual(offenders, [])

    def test_no_virtual_environment_or_egg_info_is_tracked(self) -> None:
        tracked = _git("ls-files").stdout.splitlines()
        offenders = [p for p in tracked if p.startswith(".venv/") or ".egg-info/" in p]
        self.assertEqual(offenders, [])

    def test_gitignore_prevents_recurrence(self) -> None:
        for path in (
            "skills/statistical-data-manager/python/tests/__pycache__/test_core.cpython-312.pyc",
            "skills/statistical-data-manager/python/src/suai_data_manager/__pycache__/core.cpython-313.pyc",
            "module.pyc",
            ".venv/bin/python",
            "skills/statistical-data-manager/python/src/suai_statistical_data_manager.egg-info/PKG-INFO",
        ):
            with self.subTest(path=path):
                self.assertEqual(_git("check-ignore", "-q", path).returncode, 0, f"{path} is not ignored")


if __name__ == "__main__":
    unittest.main()
