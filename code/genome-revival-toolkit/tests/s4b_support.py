"""Retain S4b commands, including failed attempts; normalize machine paths only."""
import json
import os
from pathlib import Path
import re
import subprocess
import time


class Commands:
    def __init__(self, directory, roots=()):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.roots = list(roots)
        self.roots += [(Path.home(), "<USER>"), (Path(os.environ.get("TEMP", "/tmp")), "<TEMP>")]
        self.replacements = []
        for path, label in sorted(self.roots, key=lambda row: len(str(row[0])), reverse=True):
            spellings = set()
            for value in (str(path), Path(path).as_posix(), json.dumps(str(path))[1:-1], json.dumps(Path(path).as_posix())[1:-1]):
                for _ in range(6):
                    spellings.add(value)
                    value = value.replace("\\", "\\\\")
            self.replacements.extend((re.compile(re.escape(value), re.IGNORECASE), label)
                                     for value in sorted(spellings, key=len, reverse=True))
        self.rows = []

    def safe(self, text):
        for pattern, label in self.replacements:
            text = pattern.sub(lambda _: label, text)
        return text

    def run(self, command, *, cwd, env=None, timeout=600):
        number = len(self.rows) + 1
        started = time.monotonic()
        # Write the attempted command before starting it, so interruptions remain visible.
        row = {"command": [self.safe(str(value)) for value in command], "cwd": self.safe(str(cwd)),
               "stdout": f"{number:03}.stdout.txt", "stderr": f"{number:03}.stderr.txt", "exit_code": None}
        self.rows.append(row)
        self.save()
        try:
            result = subprocess.run(command, cwd=cwd, env=env, capture_output=True,
                                    text=True, encoding="utf-8", errors="replace", timeout=timeout)
        except Exception as error:
            (self.directory / row["stderr"]).write_text(self.safe(str(error)), encoding="utf-8")
            row["exception"] = type(error).__name__
            self.save()
            raise
        (self.directory / row["stdout"]).write_text(self.safe(result.stdout), encoding="utf-8", newline="\n")
        (self.directory / row["stderr"]).write_text(self.safe(result.stderr), encoding="utf-8", newline="\n")
        row.update(exit_code=result.returncode, seconds=round(time.monotonic() - started, 3))
        self.save()
        return result

    def save(self):
        (self.directory / "commands.json").write_text(json.dumps(self.rows, indent=2) + "\n", encoding="utf-8", newline="\n")


def isolated_env():
    environment = dict(os.environ)
    for name in ("PYTHONPATH", "PYTHONHOME"):
        environment.pop(name, None)
    environment.update(PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1", PIP_DISABLE_PIP_VERSION_CHECK="1")
    return environment
