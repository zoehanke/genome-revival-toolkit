"""Export only this Kit's decorator declarations and generated Skill input contract."""
import argparse
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KIT = ROOT / "kits/genome-identity"
START, END = "<!-- GENERATED:START -->", "<!-- GENERATED:END -->"


def export(check=False):
    spec = importlib.util.spec_from_file_location("s5b_metadata_export", KIT / "capabilities/operations.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    declarations = sorted([item.declaration for item in vars(module).values()
                           if hasattr(item, "declaration")], key=lambda row: row["id"])
    documents = {KIT / "capabilities" / (row["id"].split(".")[1] + ".json"):
                 json.dumps(row, indent=2) + "\n" for row in declarations}
    lines = []
    for row in declarations:
        inputs = ", ".join(port["name"] + (" (optional)" if not port["required"] else "") for port in row["inputs"])
        params = ", ".join(name + (" (optional)" if name not in row["params"]["required"] else "")
                           for name in row["params"]["properties"]) or "none"
        lines.extend(["### " + row["id"], "", row["summary"], "",
                      "Inputs: " + inputs + ".", "", "Parameters: " + params + ".", ""])
    path = KIT / "SKILL.md"
    text = path.read_text(encoding="utf-8")
    documents[path] = text.split(START)[0] + START + "\n" + "\n".join(lines) + END + text.split(END)[1]
    different = []
    for path, content in documents.items():
        if check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                different.append(path.relative_to(ROOT).as_posix())
        else:
            path.write_text(content, encoding="utf-8", newline="\n")
    return {"different": different}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    result = export(parser.parse_args().check)
    print(json.dumps(result))
    raise SystemExit(bool(result["different"]))
