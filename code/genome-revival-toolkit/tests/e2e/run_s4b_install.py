"""Separately authorized S4b dependency installation; no unpinned transitive downloads."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tests.s4b_support import Commands, isolated_env


def provision(work, evidence):
    work = Path(work).resolve()
    work.mkdir(parents=True, exist_ok=False)
    log = Commands(evidence, [(ROOT, "<SOURCE>"), (work, "<WORK>")])
    env = isolated_env()

    def checked(arguments, cwd=work):
        process = log.run(arguments, cwd=cwd, env=env, timeout=1800)
        print(log.safe(process.stdout + process.stderr), flush=True)
        if process.returncode:
            raise RuntimeError("Command failed. Retained all output; no alternate version or retry was attempted.")
        return process

    pins = {}
    for name in ("requirements.lock", "requirements-release.lock"):
        for line in (ROOT / name).read_text(encoding="utf-8").splitlines():
            if not line.strip() or line.startswith("#"):
                continue
            match = re.fullmatch(r"([A-Za-z0-9_.-]+)==([A-Za-z0-9_.+!-]+)", line)
            if not match:
                raise ValueError("Unpinned dependency: " + name)
            key = match[1].lower().replace("_", "-")
            if key in pins and pins[key] != match[2]:
                raise ValueError("Conflicting locked versions")
            pins[key] = match[2]
    checked([sys.executable, "-X", "utf8", "-B", "-m", "venv", str(work / "venv")])
    python = work / "venv" / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    checked([str(python), "-X", "utf8", "-B", "-c",
             "import json,sys,ensurepip,pathlib,hashlib; "
             "p=next((pathlib.Path(ensurepip.__file__).parent/'_bundled').glob('pip-*.whl')); "
             "print(json.dumps({'prefix':sys.prefix,'base_prefix':sys.base_prefix,'pip_bootstrap_wheel':p.name,"
             "'bootstrap_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'system_site_packages':False}))"])
    report = work / "pip-report.json"
    checked([str(python), "-X", "utf8", "-B", "-m", "pip", "--isolated", "install", "--disable-pip-version-check",
             "--index-url", "https://pypi.org/simple", "--only-binary=:all:", "--no-deps", "--report", str(report),
             "-r", str(ROOT / "requirements-release.lock"), "-r", str(ROOT / "requirements.lock")])
    installed = json.loads(report.read_text(encoding="utf-8"))
    rows = []
    for item in installed["install"]:
        package, version = item["metadata"]["name"].lower().replace("_", "-"), item["metadata"]["version"]
        if pins.get(package) != version:
            raise AssertionError("Pip installed a version outside the authorized pins.")
        rows.append({"name": package, "version": version,
                     "sha256": item["download_info"]["archive_info"]["hashes"]["sha256"],
                     "source": item["download_info"]["url"]})
    (Path(evidence) / "dependency-sources.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    checked([str(python), "-m", "pip", "--isolated", "check"])
    checked([str(python), "-m", "pip", "--isolated", "list", "--format=json", "--disable-pip-version-check"])
    # Only these two lock files were given to pip. The backend is already an exact pin in the release lock.
    backend = json.loads(checked([str(python), "-c", "import importlib.metadata,json; print(json.dumps(importlib.metadata.version('setuptools')))" ]).stdout)
    if f'setuptools=={backend}' not in (ROOT / "pyproject.toml").read_text(encoding="utf-8"):
        raise AssertionError("Build backend differs from pyproject's exact pin.")
    return {"dependency_packages": len(rows), "backend": backend, "status": "DEPENDENCIES_INSTALLED",
            "pip_report_sha256": hashlib.sha256(report.read_bytes()).hexdigest()}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    result = provision(args.work, args.evidence)
    (args.evidence / "RESULTS.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))
