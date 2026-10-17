"""D15/D16 deterministic source ZIP and the existing build-time version provider."""
import argparse
from fnmatch import fnmatchcase
import hashlib
from importlib import metadata
import json
from pathlib import Path
import re
import subprocess
import tomllib
import zipfile
from setuptools.command.build_py import build_py

ROOT = Path(__file__).resolve().parents[1]
VERSION = json.loads(
    (ROOT / "VERSIONS.json").read_text(encoding="utf-8")
)["toolkit"]
STAMP = (1980, 1, 1, 0, 0, 0)
FORBIDDEN = {".exe", ".bin", ".dll", ".pyd", ".so", ".dylib", ".pyc", ".pyo"}
PERSONAL = re.compile(r"(?<![A-Za-z0-9])(?:[A-Za-z]:[\\/](?:Users|codex_project)[\\/]|/(?:Users|home)/[A-Za-z0-9_.\u4e00-\u9fff-]+/)")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    import rfc8785
    return rfc8785.dumps(value)


def lock_pins(items):
    result = {}
    for name, data in sorted(items.items()):
        for line in data.decode("utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            match = re.fullmatch(r"([A-Za-z0-9_.-]+)==([A-Za-z0-9_.+!-]+)", line)
            if not match:
                raise ValueError("Unpinned dependency in " + name + ": " + line)
            package = match[1].lower().replace("_", "-")
            if package in result and result[package] != match[2]:
                raise ValueError("Conflicting dependency pins: " + package)
            result[package] = match[2]
    if not result:
        raise ValueError("No locked dependencies")
    return result


def locks(root):
    return lock_pins({path.name: path.read_bytes() for path in [*root.glob("requirements*.lock"), *root.glob("requirements*.txt")]})


def third_party_pins(data):
    return {name.lower().replace("_", "-"): version for name, version in re.findall(
        r"^\|\s*([A-Za-z0-9_.-]+)\s*\|\s*([0-9][A-Za-z0-9_.+!-]*)\s*\|", data.decode("utf-8"), re.M)}


def selected(root):
    policy = json.loads((root / "ship.json").read_text(encoding="utf-8"))
    if set(policy) != {"include", "exclude"}:
        raise ValueError("ship.json needs include and exclude arrays")
    files = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        name = path.relative_to(root).as_posix()
        if any(fnmatchcase(name, pattern) for pattern in policy["include"]) and not any(fnmatchcase(name, pattern) for pattern in policy["exclude"]):
            if path.is_symlink():
                raise ValueError("D15 excludes symbolic links: " + name)
            files[name] = path.read_bytes()
    return files


def third_party(root):
    lines = ["# Third-party dependencies", "", "Generated from exact dependency pins and locally installed distribution metadata.",
             "Dependency code and compiled binaries are not bundled in this source package.", "", "| Package | Version | License metadata |", "|---|---|---|"]
    records = []
    for name, version in sorted(locks(root).items()):
        distribution = metadata.distribution(name)
        if distribution.version != version:
            raise ValueError("Installed metadata does not match lock: " + name)
        license_name = distribution.metadata.get("License-Expression") or "See the distribution license files"
        lines.append("| " + name + " | " + version + " | " + license_name.replace("|", "\\|") + " |")
        records.append((name, distribution))
    lines += ["", "## Local source records", "", "Identifiers below describe distribution metadata, not a new legal assessment."]
    for name, distribution in records:
        lines += ["", "### " + name, ""]
        for entry in sorted(distribution.files or [], key=str):
            path = str(entry).replace("\\", "/")
            if ".dist-info/" in path and "/_vendor/" not in path and Path(path).name.upper() in {"LICENSE", "LICENSE.TXT", "LICENSE.MD", "COPYING", "COPYING.TXT"}:
                lines.append("- " + path + ": SHA-256 " + digest(distribution.locate_file(entry).read_bytes()))
        for label in ("License-File", "Project-URL", "Home-page"):
            for value in distribution.metadata.get_all(label, []):
                lines.append("- " + label + ": " + value)
        if not any(Path(str(entry)).name.upper() in {"LICENSE", "COPYING", "LICENSE.TXT"} for entry in distribution.files or []):
            lines.append("- License text is not separately inventoried here; consult the locked distribution's metadata and upstream project.")
    lines += ["", "## External program", "", "Primer3 is optional and is not bundled. Its executable and thermodynamic data remain external.",
              "The toolkit records their actual identities when used. No external binary is redistributed by this build.", ""]
    return "\n".join(lines).encode("utf-8")


def payload(root):
    files = selected(root)
    policy = json.loads((root / "ship.json").read_text(encoding="utf-8"))
    for name in ("THIRD_PARTY.md", "src/dna_design_core/resources/VERSIONS.json"):
        if not any(fnmatchcase(name, pattern) for pattern in policy["include"]) or any(fnmatchcase(name, pattern) for pattern in policy["exclude"]):
            raise ValueError("ship.json must select generated release content: " + name)
    if "THIRD_PARTY.md" not in files or third_party_pins(files["THIRD_PARTY.md"]) != locks(root):
        raise ValueError("Generate and freeze THIRD_PARTY.md for the current pins before building.")
    # The existing kernel.release already supports this generated installed-package copy.
    files["src/dna_design_core/resources/VERSIONS.json"] = (root / "VERSIONS.json").read_bytes()
    return files


class ReleaseBuild(build_py):
    """Install the selected source payload without duplicating the Core implementation.

    A source wheel is an installation test, not approval of a release ZIP. When
    built from an approved ZIP, preserve that ZIP's manifest and release identity.
    """
    def run(self):
        super().run()
        files = payload(ROOT)
        rows = [{"path": name, "sha256": digest(data), "bytes": len(data)} for name, data in sorted(files.items())]
        provided = ROOT / "release-manifest.json"
        if provided.exists():
            data = provided.read_bytes()
            manifest = json.loads(data)
            if canonical(manifest) != data or manifest["files"] != rows:
                raise ValueError("Source payload differs from its supplied release manifest.")
        else:
            try:
                build_id = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                                                   text=True, encoding="utf-8", stderr=subprocess.DEVNULL).strip()
            except subprocess.CalledProcessError:
                build_id = "source-wheel"
            manifest = {"versions": json.loads((ROOT / "VERSIONS.json").read_text(encoding="utf-8")),
                        "build_id": build_id, "files": rows, "dependencies": locks(ROOT)}
            data = canonical(manifest)
        package = Path(self.build_lib) / "dna_design_core"
        for name, content in files.items():
            path = package / name.removeprefix("src/dna_design_core/")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        (package / "release-manifest.json").write_bytes(data)


def build(root, output, build_id):
    from check_release import inspect_tree
    root, output = Path(root).resolve(), Path(output).resolve()
    report = inspect_tree(root)
    if report["status"] != "PASS":
        return {"status": report["status"], "build_created": False, "checks": report}
    files = payload(root)
    manifest = {"versions": json.loads((root / "VERSIONS.json").read_text(encoding="utf-8")), "build_id": build_id,
                "files": [{"path": name, "sha256": digest(data), "bytes": len(data)} for name, data in sorted(files.items())],
                "dependencies": locks(root)}
    manifest_bytes = canonical(manifest)
    release_id = digest(manifest_bytes)
    files["release-manifest.json"] = manifest_bytes
    output.mkdir(parents=True, exist_ok=True)
    name = "genome-revival-toolkit-" + manifest["versions"]["toolkit"] + "-" + release_id
    archive = output / (name + ".zip")
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_STORED) as bundle:
        for path, data in sorted(files.items()):
            info = zipfile.ZipInfo(path, date_time=STAMP)
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            bundle.writestr(info, data)
    archive_hash = digest(archive.read_bytes())
    (output / (name + ".sha256")).write_text(archive_hash + "  " + archive.name + "\n", encoding="utf-8", newline="\n")
    (output / (name + ".manifest.json")).write_bytes(manifest_bytes)
    return {"status": "PASS", "build_created": True, "release_id": release_id, "archive": archive.name,
            "sha256": archive_hash, "manifest": name + ".manifest.json", "files": len(files), "zip_timestamp": list(STAMP)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--out", type=Path, default=ROOT / "dist/release")
    parser.add_argument("--build-id")
    parser.add_argument("--third-party-only", action="store_true")
    parser.add_argument("--version", action="store_true")
    args = parser.parse_args()
    if args.version:
        print(json.loads((args.root / "VERSIONS.json").read_text(encoding="utf-8"))["toolkit"])
        return 0
    if args.third_party_only:
        (args.root / "THIRD_PARTY.md").write_bytes(third_party(args.root))
        print(json.dumps({"generated": "THIRD_PARTY.md"}))
        return 0
    build_id = args.build_id or subprocess.check_output(["git", "-C", str(args.root), "rev-parse", "HEAD"], text=True).strip()
    result = build(args.root, args.out, build_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

