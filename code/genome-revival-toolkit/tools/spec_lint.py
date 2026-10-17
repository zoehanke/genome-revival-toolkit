#!/usr/bin/env python3
"""Spec-consistency lint for SPEC.md (prototype of the future tools/spec_lint.py).

Checks INV-S1..S6 plus cross-reference checks (INV ids, rule ids, check ids, capability counts).
It only reads the draft. Exit code 1 if any hard finding exists.
"""
import re
import sys
import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('spec', nargs='?', default=Path(__file__).resolve().parents[3]/'spec/SPEC.md')
parser.add_argument('--schemas', type=Path, default=Path(__file__).resolve().parents[1]/'src/dna_design_core/resources/schemas')
parser.add_argument('--fields-report', type=Path)
args = parser.parse_args()
path = Path(args.spec)
text = path.read_text(encoding="utf-8")
hard, soft = [], []

# split: body (before appendix C onward is fine for most checks), appendix E catalogue
idx_E = text.index("# 附录 E 日志事件目录")
idx_F = text.index("# 附录 F")
appE = text[idx_E:idx_F]
body = text[:idx_E] + text[idx_F:]            # everything except the catalogue itself
idx_check = text.find("## 合并后自检")
if idx_check != -1:
    body = body.replace(text[idx_check:], "")

# ---------- S1 event types ----------
cat = set()
for line in appE.splitlines():
    if line.startswith("|"):
        first = line.split("|")[1]
        cat |= set(re.findall(r"`([a-z_]+\.[a-z_]+)`", first))
prefixes = {"run", "goal", "input", "pipeline", "declaration", "step", "call",
            "verdict", "judge", "seal", "limit", "journal"}
used = set()
for m in re.finditer(r"`((?:%s)\.[a-z_]+)`" % "|".join(prefixes), body):
    used.add(m.group(1))
# tokens that are not events (files, check ids etc.)
not_events = {"run.json", "journal.ndjson", "kit.json", "goal.json", "run.lock", "journal.recovered_"}
used = {u for u in used if u not in not_events and not u.endswith(".json") and not u.endswith(".ndjson")}
for u in sorted(used - cat):
    # allow wildcards like step.* handled elsewhere
    hard.append(f"S1 event used in body but not in Appendix E: {u}")
for line in appE.splitlines():
    if line.startswith("| `") and len([c for c in line.split("|")]) > 3:
        writer = line.split("|")[2].strip()
        if not writer:
            hard.append(f"S1 event without writer: {line[:60]}")

# ---------- S2 verbs ----------
verbs_table = text[text.index("| 动词 | 作用 | 写日志 |"):text.index("- **请求文件**")]
table_verbs = set()
for line in verbs_table.splitlines():
    if line.startswith("| `"):
        cell = line.split("|")[1]
        first = re.findall(r"`([^`]+)`", cell)[0]
        w = re.split(r"[ \[｜<]", first.strip())
        table_verbs.add(w[0])
        if len(w) > 1 and w[0] in ("run", "pipeline", "goal", "template", "record", "kits", "review", "limit"):
            table_verbs.add(w[0] + " " + re.sub(r"[\[\]｜<>].*", "", w[1]))
mentioned = set(re.findall(r"`grt ([a-z]+)", body))
for v in sorted(mentioned):
    if v not in table_verbs:
        hard.append(f"S2 verb mentioned but not in D13 verb table: grt {v}")
# verbs used inside prose as `xxx` in backticks with known names
for v in ("judge", "seal", "verify", "doctor", "status", "declare"):
    if v not in table_verbs:
        hard.append(f"S2 expected verb missing from verb table: {v}")

# ---------- S3 module paths ----------
tree_block = text[text.index("genome-revival-toolkit/\n├─ VERSIONS.json"):text.index("- **命名**")]
pkgs = {}
cur = None
for line in tree_block.splitlines():
    m = re.search(r"│  [├└]─ ([a-z_]+)/\s+(.*)", line)
    if m:
        cur = m.group(1)
        files = set()
        for tok in re.findall(r"([a-z_]+)\.py|([a-z_]+)/|\{([a-z_,/]+)\}", m.group(2)):
            for t in tok:
                if t:
                    files |= {x.strip("/") for x in t.split(",")}
        pkgs[cur] = files
# explicit extras the tree states in prose
pkgs.setdefault("kernel", set()).update({"public", "ports"})
pkgs.setdefault("biology", set()).update({"public"})
modules = set(pkgs)
for m in re.finditer(r"`?\b(kernel|biology|storage|knowledge|catalog|capabilities|engine|assurance|record|application)\.([a-z_]+)(?:\.([a-z_]+))?", body):
    mod, sub = m.group(1), m.group(2)
    if mod not in pkgs:
        hard.append(f"S3 unknown module in path: {mod}.{sub}")
        continue
    if f"{mod}.{sub}" in cat:
        continue
    if sub not in pkgs[mod] and sub not in ("py", "md", "json"):
        soft.append(f"S3 {mod}.{sub} is not a file/dir listed in the D15 tree (API name? check)")

# ---------- S4 rule-id prefixes and cross references ----------
allowed = {"DEP", "GOL", "REV", "KIT", "SEAL", "RV", "TST", "DEV", "ADV", "INV", "MVP", "SHA", "UTF"}
defined = {}
for m in re.finditer(r"\b([A-Z]{2,4})-(\d+)\b", text):
    defined.setdefault(m.group(1), set()).add(int(m.group(2)))
for p in defined:
    if p not in allowed:
        soft.append(f"S4 unknown rule prefix: {p}-")
inv_defined = set(re.findall(r"^\| (INV-[A-Z]+\d+) \|", text, flags=re.M))
inv_used = set(re.findall(r"INV-[A-Z]+\d+", body))
for i in sorted(inv_used - inv_defined):
    hard.append(f"S4 INV referenced but not defined in Appendix C: {i}")
# ranges like INV-C1…INV-C7 are expanded manually; also check range endpoints exist
for m in re.finditer(r"(INV-[A-Z]+)(\d+)…(?:INV-[A-Z]+)?(\d+)", body):
    for n in (m.group(2), m.group(3)):
        if f"{m.group(1)}{n}" not in inv_defined:
            hard.append(f"S4 INV range endpoint missing: {m.group(1)}{n}")
for fam, hi in (("DEP", 13), ("GOL", 8), ("REV", 9), ("KIT", 7), ("SEAL", 10), ("RV", 7), ("TST", 11), ("DEV", 14), ("ADV", 24)):
    nums = {int(x) for x in re.findall(rf"(?<![A-Z]){fam}-(\d+)", text)}
    if nums and max(nums) > hi:
        hard.append(f"S4 {fam}-{max(nums)} exceeds defined range {fam}-1..{hi}")
    if not nums:
        soft.append(f"S4 family {fam} never used")

# ---------- S5 retired terms ----------
retired = ["assessor", "检查器", "plan-time", "step-time", "result-time", "seal-time", "post-seal", "INCONCLUSIVE",
           "delivery_classes", "kits_runtime", "kit-v3", "RunSession", "交付类别", "deliver_as", "成熟", "mature",
           "SEQUENCE", "PREPARATION", "ARTIFACT", "`PLAN`", "DOMAIN", "五个阶段", "5 个阶段", "六个范围", "五种结果",
           "subject_kind", "尝试序号", "--retry", "catalog.pinned", "environment.recorded", "kit.loaded", "verification_primers",
           "EXPERIMENTAL", "emit_note", "stage.exported", "artifact.registered",
           "exploratory", "request_id", "cancel_step", "replace_pending_step", "state.json",
           "NETWORK_FORBIDDEN", "surface"]
neg_ctx = re.compile(r"(没有|不含|不得|不能|不允许|取消|退役|不采用|旧|不是|去掉|不再|无)")
for t in retired:
    for m in re.finditer(re.escape(t), body):
        if t in ("成熟", "mature") and re.match(r"成熟(度|方法)", body[m.start():m.start()+4]):
            continue
        s = body.rfind("\n", 0, m.start()) + 1
        e = body.find("\n", m.end())
        line = body[s:e]
        if neg_ctx.search(line):
            soft.append(f"S5 retired term '{t}' in a negating/legacy context (ok to eyeball): {line.strip()[:110]}")
        else:
            hard.append(f"S5 retired term '{t}' used affirmatively: {line.strip()[:130]}")

# ---------- S6 counts ----------
vocab = text[text.index("## 1. 词表"):text.index("**可信度的三个问题")]
def cell(label):
    m = re.search(rf"\| {re.escape(label)}[^|]*\| ([^\n]*) \|", vocab)
    return re.findall(r"`([A-Za-z_]+)`", m.group(1)) if m else []
moments = cell("检查时刻")
outcomes = cell("裁决结果")
scopes = cell("裁决范围")
roles = cell("能力角色")
issuers = cell("裁决出具者")
counts = {"moments": len(moments), "outcomes": len(outcomes), "scopes": len(scopes), "capability roles": len(roles), "issuers": len(issuers)}
expected = {"moments": 3, "outcomes": 4, "scopes": 4, "capability roles": 2, "issuers": 3}
for k, v in expected.items():
    if counts[k] != v:
        hard.append(f"S6 vocabulary count mismatch: {k} = {counts[k]} (expected {v})")

# ---------- check ids ----------
core_checks = set()
d7 = text[text.index("*核心检查目录"):text.index("*必过项（obligations）")]
core_checks |= set(re.findall(r"`(check\.[a-z_]+)`", d7))
kinds = ["topology", "exact_sequence", "components_present", "components_absent", "regions_unchanged",
         "output_present", "claim_reported"]
core_checks |= {f"check.goal.{k}" for k in kinds} | {"check.goal.target_role_met", "check.goal.nonempty"}
used_checks = set(re.findall(r"`(check\.[a-z_.]+?)(?:@[0-9.]+)?`", body))
for c in sorted(used_checks):
    c2 = c.rstrip(".")
    if c2 not in core_checks and c2 not in ("check.goal", "check.goal.<kind>"):
        hard.append(f"CHK check id used but not in core catalogue: {c2}")
if "check.goal_nonempty" in body:
    hard.append("CHK inconsistent id spelling: check.goal_nonempty (use check.goal.nonempty)")

# ---------- CHK2 naming convention (INV-C8) ----------
known_check_roles = {"cut_plasmid.check_direction", "cut_plasmid.check_pam", "cut_plasmid.check_vector_self_target",
                     "evidence.check_record_consistency"}
for m in set(re.findall(r"([a-z_]+\.check_[a-z_]+)", body)):
    if m not in known_check_roles:
        hard.append(f"CHK2 id with check_ prefix that is not a known CHECK-role capability: {m}")
for m in ("cut_plasmid.inspect_guide", "cut_plasmid.replace_spacer", "cut_plasmid.assess_selection"):
    if re.search(rf"{re.escape(m)}.*role.*CHECK", body):
        hard.append(f"CHK2 ACTION id described as CHECK: {m}")

# ---------- misc structural ----------
mods = re.findall(r"^\| L\d \| `([a-z_]+)` \|", text, flags=re.M)
if len(set(mods)) != 10:
    hard.append(f"D1 module table lists {len(set(mods))} modules (text says 10): {sorted(set(mods))}")
if "十一个模块" in body or "十二个模块" in body:
    hard.append("D1 states a module count different from the table")
if "十个模块" not in text:
    soft.append("D1 should say 十个模块")

from schema_alignment import compare
field_rows,field_counts=compare(text,args.schemas)
for row in field_rows:
    message=f"A fields {row['schema']}:{row['field']} {row['kind']} ({row['status']})"
    (hard if row['status']=='unresolved' else soft).append(message)
if args.fields_report:
    args.fields_report.write_text(json.dumps({'counts':field_counts,'differences':field_rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')

print(f"== spec_lint on {path.name}: {len(text)} chars ==")
print(f"Appendix field alignment: {field_counts}")
print(f"vocab counts: {counts}")
print(f"events in Appendix E: {len(cat)}; events mentioned in body: {len(used)}")
print(f"INV defined: {len(inv_defined)}; referenced in body: {len(inv_used)}")
print(f"\nHARD findings: {len(hard)}")
for h in hard:
    print("  -", h)
print(f"\nSOFT findings: {len(soft)}")
for s in soft:
    print("  -", s)
sys.exit(1 if hard else 0)
