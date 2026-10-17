"""Read-only Linux availability check. Never installs or starts a distribution."""
import json
from pathlib import Path
import shutil
import subprocess
import sys

output = Path(sys.argv[1])
output.mkdir(parents=True, exist_ok=False)
program = shutil.which("wsl.exe")
rows = []
if program:
    for arguments in (["--list", "--verbose"], ["--list", "--quiet"]):
        process = subprocess.run([program, *arguments], capture_output=True, timeout=30)
        def decode(data):
            if data.startswith((b"\xff\xfe", b"\xfe\xff")):
                return data.decode("utf-16")
            return data.decode("utf-16-le" if b"\0" in data[:200] else "utf-8", errors="replace")
        stdout, stderr = decode(process.stdout), decode(process.stderr)
        name = str(len(rows) + 1)
        (output / (name + ".stdout.txt")).write_text(stdout, encoding="utf-8", newline="\n")
        (output / (name + ".stderr.txt")).write_text(stderr, encoding="utf-8", newline="\n")
        rows.append({"command": ["wsl.exe", *arguments], "exit_code": process.returncode,
                     "stdout": name + ".stdout.txt", "stderr": name + ".stderr.txt"})
result = {"commands": rows, "wsl_command_found": bool(program),
          "linux_execution": "NOT_PERFORMED", "installation": "NOT_PERFORMED",
          "scope": "Local WSL list only; no image download or distribution startup."}
(output / "RESULTS.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result))
