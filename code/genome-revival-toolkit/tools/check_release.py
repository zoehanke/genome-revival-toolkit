"""D15/D16 INV-F10 checks for source trees and deterministic release archives."""
import argparse
import ast
import json
from pathlib import Path
import re
import subprocess
import tomllib
import zipfile

from build_release import FORBIDDEN, PERSONAL, ROOT, canonical, digest, lock_pins, locks, payload, third_party_pins

APACHE_SHA256 = "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30"
LIMIT = 50_000_000
PLACEHOLDER = "【待用户填写】"
SECTIONS = ("Purpose", "Audience", "Installation and running", "Reproduce the main results", "AI use disclosure", "License", "CI status")


def tracked(root):
    repository = Path(subprocess.check_output(["git", "-C", str(root), "rev-parse", "--show-toplevel"], text=True).strip())
    names = subprocess.check_output(["git", "-C", str(repository), "ls-files", "-z"]).decode("utf-8").split("\0")
    return [(repository / name, name) for name in names if name]


def inspect_tree(root, *, require_git=True):
    root = Path(root).resolve()
    findings = []
    def fail(item, message):
        findings.append({"check": item, "message": message})
    license_path = root / "LICENSE"
    actual = digest(license_path.read_bytes()) if license_path.is_file() else None
    if actual != APACHE_SHA256:
        fail("license", "LICENSE must match the pinned Apache-2.0 full-text SHA-256.")
    readme = (root / "README.md").read_text(encoding="utf-8") if (root / "README.md").is_file() else ""
    parts = re.split(r"^## ([^\n]+)\n", readme, flags=re.M)
    sections = dict(zip((name.strip() for name in parts[1::2]), parts[2::2]))
    for section in SECTIONS:
        if section not in sections:
            fail("readme", "Missing required README section: " + section)
        elif not sections[section].strip():
            fail("readme", "Empty required README section: " + section)
    if "官方 GitLab CI 未执行" not in readme:
        fail("readme", "README must state 官方 GitLab CI 未执行.")
    try:
        dependencies = locks(root)
    except (ValueError, OSError) as error:
        dependencies = {}
        fail("dependencies", str(error))
    try:
        versions = json.loads((root / "VERSIONS.json").read_text(encoding="utf-8"))
        project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
        if "version" in project["project"] or "version" not in project["project"].get("dynamic", []):
            raise ValueError("pyproject must derive its version from VERSIONS.json")
        if project["tool"]["setuptools"]["dynamic"]["version"] != {"attr": "tools.build_release.VERSION"}:
            raise ValueError("Unsupported version provider")
        provider = ast.parse((root / "tools/build_release.py").read_text(encoding="utf-8"))
        version_node = next(node.value for node in provider.body if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "VERSION" for target in node.targets))
        if not isinstance(version_node, ast.Subscript) or ast.literal_eval(version_node.slice) != "toolkit" or not re.fullmatch(r"\d+\.\d+\.\d+(?:[a-zA-Z0-9.+-]*)", versions["toolkit"]):
            raise ValueError("Version provider must read the toolkit key, not a second version literal")
    except (OSError, ValueError, KeyError, StopIteration, SyntaxError) as error:
        fail("versions", str(error))
    try:
        rows = tracked(root) if require_git else []
    except subprocess.CalledProcessError:
        rows = []
        fail("tracked_size", "Git tracked-file inventory is unavailable.")
    size = sum(path.stat().st_size for path, _ in rows if path.is_file())
    if size >= LIMIT:
        fail("tracked_size", "Git tracked files reach the 50,000,000-byte limit.")
    for path, name in rows:
        if path.suffix.lower() in FORBIDDEN:
            fail("compiled", "Prohibited tracked artifact: " + name)
    try:
        files = payload(root)
        for name, data in files.items():
            if Path(name).suffix.lower() in FORBIDDEN:
                fail("compiled", "Prohibited selected artifact: " + name)
            if PERSONAL.search(data.decode("utf-8", errors="ignore")):
                fail("personal_paths", "Machine-specific personal path in selected file: " + name)
    except (OSError, ValueError) as error:
        files = {}
        fail("ship", str(error))
    placeholders = {name: data.decode("utf-8").count(PLACEHOLDER) for name, data in files.items()
                    if name == "README.md" or name.startswith("docs/judges/")}
    placeholders = {name: count for name, count in placeholders.items() if count}
    count = sum(placeholders.values())
    return {"status": "FAIL" if findings else "INCOMPLETE" if count else "PASS", "findings": findings,
            "placeholder_count": count, "placeholder_files": placeholders, "tracked_bytes": size, "tracked_limit_bytes": LIMIT,
            "tracked_files": len(rows), "selected_files": len(files), "license_sha256": actual, "dependencies": dependencies,
            "scope": "INV-F10 source inventory and payload hygiene; not S4 approval or scientific acceptance."}


def inspect_zip(path):
    findings = []
    with zipfile.ZipFile(path) as bundle:
        names = bundle.namelist()
        manifest_bytes = bundle.read("release-manifest.json")
        manifest = json.loads(manifest_bytes)
        expected = {row["path"]: row for row in manifest["files"]}
        if len(names) != len(set(names)) or set(names) != set(expected) | {"release-manifest.json"}:
            findings.append("Archive file membership differs from the manifest.")
        for name in names:
            if Path(name).suffix.lower() in FORBIDDEN:
                findings.append("Prohibited compiled artifact: " + name)
            if name.startswith("/") or ".." in Path(name).parts or "\\" in name:
                findings.append("Unsafe archive member: " + name)
            if name in expected and (digest(bundle.read(name)) != expected[name]["sha256"] or len(bundle.read(name)) != expected[name]["bytes"]):
                findings.append("File bytes differ: " + name)
            if bundle.getinfo(name).date_time != (1980, 1, 1, 0, 0, 0):
                findings.append("Archive timestamp is not fixed: " + name)
        if names != sorted(names):
            findings.append("Archive entries are not sorted.")
        if "LICENSE" not in names or digest(bundle.read("LICENSE")) != APACHE_SHA256:
            findings.append("Archive LICENSE differs from the Apache-2.0 reference.")
        readme = bundle.read("README.md").decode("utf-8") if "README.md" in names else ""
        parts = re.split(r"^## ([^\n]+)\n", readme, flags=re.M)
        sections = dict(zip(parts[1::2], parts[2::2]))
        if any(not sections.get(section, "").strip() for section in SECTIONS) or "官方 GitLab CI 未执行" not in readme:
            findings.append("Archive README lacks required content.")
        if not any(name.startswith("requirements") and name.endswith((".lock", ".txt")) for name in names):
            findings.append("Archive lacks locked dependencies.")
        try:
            dependencies = lock_pins({name: bundle.read(name) for name in names if "/" not in name and name.startswith("requirements") and name.endswith((".lock", ".txt"))})
            if dependencies != manifest["dependencies"]:
                findings.append("Archive dependency locks differ from the manifest.")
            if third_party_pins(bundle.read("THIRD_PARTY.md")) != dependencies:
                findings.append("Archive third-party inventory differs from its dependency locks.")
            versions = json.loads(bundle.read("VERSIONS.json"))
            if versions != manifest["versions"] or json.loads(bundle.read("src/dna_design_core/resources/VERSIONS.json")) != versions:
                findings.append("Archive version sources differ.")
            project = tomllib.loads(bundle.read("pyproject.toml").decode("utf-8"))
            if "version" in project["project"] or project["tool"]["setuptools"]["dynamic"]["version"] != {"attr": "tools.build_release.VERSION"}:
                findings.append("Archive pyproject uses a different version source.")
        except (KeyError, ValueError) as error:
            findings.append("Archive dependency/version declaration is invalid: " + str(error))
        placeholders = sum(bundle.read(name).decode("utf-8").count(PLACEHOLDER) for name in names if name == "README.md" or name.startswith("docs/judges/"))
        if placeholders:
            findings.append("Archive still contains user placeholders: " + str(placeholders))
        if canonical(manifest) != manifest_bytes:
            findings.append("Manifest is not the canonical JSON used for release identity.")
    return {"status": "FAIL" if findings else "PASS", "findings": findings, "release_id": digest(manifest_bytes), "archive_sha256": digest(Path(path).read_bytes())}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--zip", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    result = inspect_zip(args.zip) if args.zip else inspect_tree(args.root)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "PASS" else 2 if result["status"] == "INCOMPLETE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
