"""S3 declarations, source handling, Kit structure and generated contracts."""
from copy import deepcopy
import inspect
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from revival_support import KIT, ROOT, context_for, load_kit, skill_contract
from dna_design_core.catalog.registry import Catalog
from dna_design_core.kernel import schemas


class EvidenceContracts(unittest.TestCase):
    def test_declarations_exported_from_decorators_and_signatures(self):
        module = load_kit()
        for path in (KIT / "capabilities").glob("*.json"):
            declaration = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(schemas.issues("capability-v1", declaration), [])
            function = getattr(module, path.stem)
            self.assertEqual(function.declaration, declaration)
            for port in declaration["inputs"] + declaration["outputs"]:
                if port["type"] == "document":
                    self.assertIn("schema", port)
                    self.assertNotIn("schema_ref", port)
            permitted = {"ctx"} | {row["name"] for row in declaration["inputs"]} | set(declaration["params"]["properties"])
            self.assertEqual(set(inspect.signature(function).parameters), permitted)

    def test_contributions_match_files_and_dependencies_are_declared(self):
        manifest = json.loads((KIT / "kit.json").read_text(encoding="utf-8"))
        self.assertEqual(schemas.issues("kit-v1", manifest), [])
        for kind, directory in [("capabilities", "capabilities"), ("knowledge", "knowledge"), ("templates", "templates"), ("text", "text")]:
            actual = {path.relative_to(KIT).as_posix() for path in (KIT / directory).glob("*.json")}
            self.assertEqual(actual, set(manifest["contributes"][kind]))
        self.assertFalse(Catalog().problems)
        for capability in Catalog().describe("capabilities"):
            if capability["id"].startswith("evidence."):
                self.assertTrue(all(row["type"] != "material" for row in capability["inputs"] + capability["outputs"]))

    def test_each_truth_table_row_has_identifiable_source(self):
        for path in (KIT / "knowledge").glob("*.json"):
            rule = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(schemas.issues("rule-v1", rule), [])
            self.assertEqual(rule["source"]["verification_status"], "unverified")
            self.assertNotIn("verification_receipt", rule["source"])
            self.assertTrue(rule["source"]["supports"] and rule["source"]["does_not_support"])
            for row in rule["parameters"]["truth_table"]:
                self.assertEqual(row["source_ref"], rule["id"])
            for bad_class in ("AI", "internet", "latest"):
                bad = deepcopy(rule)
                bad["source"]["source_class"] = bad_class
                self.assertTrue(schemas.issues("rule-v1", bad))

    def test_unattributed_candidates_remain_draft_and_cannot_load(self):
        candidates = json.loads((KIT / "knowledge/drafts/unattributed.json").read_text(encoding="utf-8"))["candidates"]
        for row in candidates:
            self.assertEqual(row["status"], "draft")
            self.assertEqual(row["verification_status"], "unverified")
            self.assertIsNone(row["source"])
            self.assertTrue(schemas.issues("rule-v1", row))
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "bad-kit"
            shutil.copytree(KIT, root)
            rule = json.loads((root / "knowledge/functional_revival.json").read_text(encoding="utf-8"))
            rule["status"] = "draft"
            rule["source"] = None
            (root / "knowledge/functional_revival.json").write_text(json.dumps(rule), encoding="utf-8")
            with patch("dna_design_core.catalog.registry.BUNDLED", Path(folder) / "empty"):
                catalog = Catalog([root])
            self.assertEqual(catalog.problems[0]["code"], "KNOWLEDGE_SOURCE_INVALID")
            self.assertFalse(any(name.startswith("evidence.") for name in catalog.entries))

    def test_template_and_generated_skill_contract(self):
        value = json.loads((KIT / "templates/assess_observations.json").read_text(encoding="utf-8"))
        self.assertEqual(schemas.issues("pipeline-template-v1", value), [])
        self.assertEqual([row["use"] for row in value["steps"]], ["evidence.parse_observations", "evidence.assess_observations"])
        skill = (KIT / "SKILL.md").read_text(encoding="utf-8")
        generated = skill.split("<!-- GENERATED:START -->\n")[1].split("<!-- GENERATED:END -->")[0]
        self.assertEqual(generated, skill_contract())

    def test_frozen_knowledge_pack_ids_match_manifest(self):
        module = load_kit()
        manifest = json.loads((KIT / "kit.json").read_text(encoding="utf-8"))
        expected = {"kit:revival-evidence/" + name for name in manifest["contributes"]["knowledge"]}
        self.assertEqual(set(module.read_rules.__globals__["RULE_PACKS"]), expected)
        self.assertEqual(len(module.read_rules(context_for())), len(expected))

    def test_inline_schemas_reject_missing_counts_and_claim_status(self):
        module = load_kit()
        document = module.parse_observations(None, KIT / "examples/b3.csv").documents["document"]
        parsed_schema = module.parse_observations.declaration["outputs"][0]["schema"]
        self.assertEqual(schemas.issues(parsed_schema, document), [])
        del document["observations"][0]["colonies"]
        self.assertTrue(schemas.issues(parsed_schema, document))
        document = module.parse_observations(None, KIT / "examples/b3.csv").documents["document"]
        report = module.assess_observations(context_for(), document).documents["assessment"]
        report_schema = module.assess_observations.declaration["outputs"][0]["schema"]
        self.assertEqual(schemas.issues(report_schema, report), [])
        del report["conclusions"][0]["status"]
        self.assertTrue(schemas.issues(report_schema, report))


if __name__ == "__main__":
    unittest.main()
