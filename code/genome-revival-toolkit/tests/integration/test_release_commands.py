"""Public release-tool commands on a labelled synthetic source fixture; installation stays unperformed."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests"))
from release_fixture import source_tree


class ReleaseCommandTests(unittest.TestCase):
    def test_build_check_and_no_install_plan_through_command_line(self):
        with tempfile.TemporaryDirectory(prefix="s4a_cli_") as directory:
            root = Path(directory)
            source = source_tree(root / "source")
            commands = []
            def command(name, *arguments):
                process = subprocess.run([sys.executable, "-X", "utf8", "-B", str(ROOT / "tools" / name), *map(str, arguments)],
                    capture_output=True, text=True, encoding="utf-8", timeout=60)
                self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
                value = json.loads(process.stdout)
                commands.append({"tool": name, "exit_code": process.returncode, "result": value})
                return value
            first = command("build_release.py", "--root", source, "--out", root / "a", "--build-id", "synthetic-public-command")
            second = command("build_release.py", "--root", source, "--out", root / "b", "--build-id", "synthetic-public-command")
            self.assertEqual(first, second)
            archive = root / "a" / first["archive"]
            checked = command("check_release.py", "--zip", archive)
            self.assertEqual(checked["status"], "PASS")
            self.assertEqual(checked["release_id"], first["release_id"])
            proposed = command("clean_env_verify.py", "--archive", archive, "--workdir", root / "fresh")
            self.assertEqual(proposed["status"], "NOT_PERFORMED")
            self.assertFalse((root / "fresh").exists())
            folder = ROOT / "tests/evidence/s4a"
            folder.mkdir(parents=True, exist_ok=True)
            (folder / "public-commands.json").write_text(json.dumps({"scope": "Synthetic fixture, not a team release or installed environment.",
                "commands": commands, "two_archive_bytes_equal": (root / "a" / first["archive"]).read_bytes() == (root / "b" / second["archive"]).read_bytes()}, indent=2) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    unittest.main()
