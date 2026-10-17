"""Independent minimal source-tree constructions for release-engineering checks."""
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
HEADINGS = ("Purpose", "Audience", "Installation and running", "Reproduce the main results", "AI use disclosure", "License", "CI status")


def write(root, name, value):
    path = Path(root) / name
    path.parent.mkdir(parents=True, exist_ok=True)
    data = value if isinstance(value, str) else json.dumps(value, indent=2) + "\n"
    path.write_text(data, encoding="utf-8", newline="\n")
    return path


def source_tree(root):
    root = Path(root)
    root.mkdir(parents=True)
    shutil.copyfile(ROOT / "LICENSE", root / "LICENSE")
    write(root, "README.md", "# Synthetic engineering fixture\n\n" + "\n".join("## " + section + "\n\nSynthetic test content.\n" for section in HEADINGS) + "\n官方 GitLab CI 未执行。\n")
    write(root, "VERSIONS.json", {"toolkit": "0.0.0", "core": "0.0.0", "kits": {}, "schemas": {}})
    write(root, "pyproject.toml", '[project]\nname="synthetic-release-fixture"\ndynamic=["version"]\n[tool.setuptools.dynamic]\nversion={attr="tools.build_release.VERSION"}\n')
    write(root, "requirements.lock", "rfc8785==0.1.4\n")
    write(root, "THIRD_PARTY.md", "# Synthetic third-party fixture\n\n| Package | Version | Note |\n| rfc8785 | 0.1.4 | Synthetic dependency record for engineering tests. |\n")
    write(root, "src/dna_design_core/__init__.py", 'LABEL = "synthetic source fixture"\n')
    write(root, "ship.json", {"include": ["src/**", "tools/**", "docs/judges/**", "README.md", "LICENSE", "VERSIONS.json", "pyproject.toml", "ship.json", "requirements.lock", "THIRD_PARTY.md"], "exclude": []})
    (root / "tools").mkdir(exist_ok=True)
    shutil.copyfile(ROOT / "tools/build_release.py", root / "tools/build_release.py")
    subprocess.run(["git", "init", "-q", str(root)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(root), "add", "--", "."], check=True, capture_output=True)
    return root
