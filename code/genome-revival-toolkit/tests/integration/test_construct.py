"""Independent constructed donor/assay answers through actual public runs."""
import ast
from copy import deepcopy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from dna_design_core.application.api import call
from dna_design_core.biology.public import inspect_cds
from dna_design_core.catalog.registry import Catalog
from dna_design_core.engine.loading import Loader
from dna_design_core.kernel import schemas
from dna_design_core.kernel.public import material_id
from tests.construct_runtime import CASE, KIT, ROOT, checked, create, retained
from tests.oracles.construct_verify import rc, verify_run


class ConstructTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.folder = tempfile.TemporaryDirectory()
        cls.services = {}
        for method in ("gibson", "pcr"):
            service, _, result = create(Path(cls.folder.name) / method, method)
            if result["problems"]:
                raise AssertionError(result)
            cls.services[method] = service

    @classmethod
    def tearDownClass(cls):
        cls.folder.cleanup()

    def test_declarations_are_exported_from_functions_and_models_are_independent(self):
        catalog, loader = Catalog(), Loader()
        self.assertEqual(catalog.problems, [])
        for identity, entry in catalog.entries.items():
            if not identity.startswith("construct."):
                continue
            schemas.require("capability-v1", entry["declaration"])
            self.assertEqual(loader.load(entry).declaration, entry["declaration"])
            for path in entry["declaration"].get("fixtures", {}).values():
                self.assertTrue((KIT / path).is_file())
        for filename in ("model.py", "design.py"):
            source = (KIT / "capabilities" / filename).read_text(encoding="utf-8")
            imports = [node.module or "" for node in ast.walk(ast.parse(source)) if isinstance(node, ast.ImportFrom)]
            self.assertNotIn("model" if filename == "design.py" else "design", imports)
            if filename == "model.py":
                self.assertFalse(any(name.startswith("dna_design_core.biology") for name in imports), imports)

    def test_both_actual_preparation_routes_match_construction(self):
        for method, service in self.services.items():
            with self.subTest(method=method):
                result = retained(service)
                product, edited = result["materials"]["product"][0], result["materials"]["edited"][0]
                self.assertEqual(product["sequence"], CASE["expected_donor"])
                self.assertEqual(len(product["sequence"]), 190)
                self.assertEqual(edited["sequence"], CASE["expected_edited"])
                self.assertEqual(result["documents"]["route"]["laboratory_status"], "NOT_PERFORMED")
                self.assertEqual(checked(service, "check.model_agreement")["outcome"], "PASS")
                for identity in ("construct.check_preparation", "construct.check_junction_assay"):
                    fixture = json.loads((KIT / "capabilities/fixtures" / (identity + ".pass.json")).read_text(encoding="utf-8"))
                    self.assertEqual(fixture["scenario"], "valid_gibson")
                    self.assertEqual(checked(service, identity)["outcome"], fixture["expected"])

    def test_external_junctions_are_90_bp_only_on_edited_reference(self):
        for service in self.services.values():
            assay = retained(service, "assay")["documents"]["assay"]
            self.assertEqual(assay["warnings"], [])
            for background in assay["backgrounds"]:
                for pair in background["predictions"]:
                    self.assertEqual(pair["product_count"], 1 if background["id"] == "edited" else 0)
                    self.assertEqual(pair["product_bp"], 90 if background["id"] == "edited" else None)

    def test_independent_output_file_oracle_for_both_routes(self):
        for service in self.services.values():
            result = verify_run(service.root)
            self.assertTrue(result["passed"], result)
            self.assertEqual(result["donor_bp"], 190)

    def test_handoff_schema_and_executor_file_hash(self):
        for service in self.services.values():
            completed = retained(service, "handoff")
            artifact = completed["artifacts"][0]
            value = json.loads((service.root / artifact["run_path"]).read_text(encoding="utf-8"))
            declaration = service.catalog.declaration("construct.export_handoff")
            schema = next(p["schema"] for p in declaration["outputs"] if p["name"] == "handoff_data")
            schemas.require(schema, value)
            self.assertEqual(set(value), {"schema", "references", "regions", "primers"})
            self.assertTrue(all(set(row) == {"id", "sha256", "role"} for row in value["references"]))

    def test_bad_arm_bounds_halt_before_any_preparation(self):
        def change(plan):
            for step in plan["steps"]:
                if step["step_id"] in ("model", "design"):
                    step["params"]["start"] = 30
        with tempfile.TemporaryDirectory() as directory:
            service, _, result = create(directory, modify_plan=change)
            self.assertEqual(result["state"], "HALTED")
            self.assertEqual(result["problems"][0]["code"], "PLAN_PARAM_INVALID")
            self.assertFalse(service.session.steps()["design"]["started"])
            self.assertFalse(any(e["type"] == "call.recorded" for e in service.session.events()))

    def test_actual_pcr_template_mismatch_is_caught_by_model(self):
        sequence = "".join((KIT / "examples/donor-template.fasta").read_text(encoding="utf-8").splitlines()[1:])
        changed = sequence[:100] + ("A" if sequence[100] != "A" else "C") + sequence[101:]
        with tempfile.TemporaryDirectory() as directory:
            service, _, result = create(directory, "pcr", sequences={"donor-template": changed})
            self.assertEqual(result["state"], "COMPLETED")
            self.assertEqual(checked(service, "check.model_agreement")["outcome"], "FAIL")
            # Physical sequence preparation followed that wrong template correctly.
            self.assertEqual(checked(service, "construct.check_preparation")["outcome"], "PASS")
            self.assertFalse(verify_run(service.root)["passed"])

    def test_both_model_paths_one_base_source_mutations_are_detected(self):
        for path in ("model", "design"):
            with self.subTest(path=path), tempfile.TemporaryDirectory() as directory:
                folder = Path(directory)
                clone = folder / "mutated-kit"
                shutil.copytree(KIT, clone, ignore=shutil.ignore_patterns("__pycache__"))
                source = clone / "capabilities" / (path + ".py")
                text = source.read_text(encoding="utf-8")
                anchor = "    return Outcome(products={\"product\": product})" if path == "model" else "    edited, _ = replace_material_region(reference, start, end, selected)"
                mutation = '    product["sequence"] = ("A" if product["sequence"][0] != "A" else "C") + product["sequence"][1:]\n'
                self.assertEqual(text.count(anchor), 1)
                source.write_text(text.replace(anchor, mutation + anchor), encoding="utf-8", newline="\n")
                with patch("dna_design_core.catalog.registry.BUNDLED", folder / "no-bundled-kits"):
                    service, _, result = create(folder / "case", "pcr", kit_dirs=[clone])
                    self.assertEqual(result["state"], "COMPLETED")
                    self.assertEqual(checked(service, "check.model_agreement")["outcome"], "FAIL")
                    if path == "design":
                        fixture = json.loads((KIT / "capabilities/fixtures/construct.check_preparation.fail.json").read_text(encoding="utf-8"))
                        self.assertEqual(fixture["scenario"], "mutated_preparation_product")
                        self.assertEqual(checked(service, "construct.check_preparation")["outcome"], fixture["expected"])

    def test_inside_arm_primers_warn_and_fail(self):
        reference = "".join((KIT / "examples/reference.fasta").read_text(encoding="utf-8").splitlines()[1:])
        sequences = [("inside_forward", reference[50:70]), ("inside_reverse", rc(reference[190:210]))]
        primers = {"schema": "primer-set-v1", "primers": [{"id": name, "sequence": seq, "core_length": 20, "purpose": "junction_qc"}
                   for name, seq in sequences], "pairs": [{"id": "inside_arms", "forward": "inside_forward", "reverse": "inside_reverse"}]}
        with tempfile.TemporaryDirectory() as directory:
            service, _, result = create(directory, primers=primers)
            self.assertEqual(result["state"], "COMPLETED")
            report = retained(service, "assay")["documents"]["assay"]
            self.assertTrue(any("residual donor DNA also yields a band" in text for text in report["warnings"]))
            self.assertEqual(next(row for row in report["backgrounds"] if row["id"] == "donor")["predictions"][0]["product_bp"], 190)
            fixture = json.loads((KIT / "capabilities/fixtures/construct.check_junction_assay.fail.json").read_text(encoding="utf-8"))
            self.assertEqual(fixture["scenario"], "donor_carryover")
            self.assertEqual(checked(service, "construct.check_junction_assay")["outcome"], fixture["expected"])
            self.assertFalse(verify_run(service.root)["passed"])

    def test_repeated_site_is_not_hidden_by_one_product(self):
        reference = "".join((KIT / "examples/reference.fasta").read_text(encoding="utf-8").splitlines()[1:])
        repeated = reference[:250] + reference[30:50] + reference[270:]
        with tempfile.TemporaryDirectory() as directory:
            service, _, result = create(directory, sequences={"reference": repeated})
            self.assertEqual(result["state"], "COMPLETED")
            report = retained(service, "assay")["documents"]["assay"]
            left = next(row for row in report["backgrounds"] if row["id"] == "edited")["predictions"][0]
            self.assertEqual((left["product_count"], left["forward_sites"]), (1, 2))
            self.assertEqual(checked(service, "construct.check_junction_assay")["outcome"], "FAIL")

    def test_repeated_preparation_site_halts_with_registered_error(self):
        reference = "".join((KIT / "examples/reference.fasta").read_text(encoding="utf-8").splitlines()[1:])
        repeated = reference[:250] + reference[50:70] + reference[270:]
        with tempfile.TemporaryDirectory() as directory:
            service, _, result = create(directory, sequences={"reference": repeated})
            self.assertEqual(result["state"], "HALTED")
            self.assertEqual(result["problems"][0]["code"], "PLAN_PARAM_INVALID")
            self.assertEqual(service.session.steps()["design"]["state"], "FAILED")
            self.assertNotIn("checked_scope", str(result))

    def test_deletion_without_cargo_is_prepared_and_flanking_sizes_differ(self):
        def deletion(plan):
            for step in plan["steps"]:
                if step["step_id"] in ("model", "design"):
                    step["params"]["cargo_end"] = 0
        with tempfile.TemporaryDirectory() as directory:
            service, _, result = create(directory, modify_plan=deletion)
            self.assertEqual(result["state"], "COMPLETED")
            reference = "".join((KIT / "examples/reference.fasta").read_text(encoding="utf-8").splitlines()[1:])
            self.assertEqual(retained(service)["materials"]["product"][0]["sequence"], reference[50:100] + reference[160:210])
            report = retained(service, "assay")["documents"]["assay"]
            self.assertEqual([row["predictions"][0]["product_bp"] for row in report["backgrounds"]], [200, 140, None])
            self.assertEqual(checked(service, "check.model_agreement")["outcome"], "PASS")
            self.assertEqual(checked(service, "construct.check_junction_assay")["outcome"], "PASS")
            self.assertTrue(verify_run(service.root)["passed"])

    def test_linear_gibson_preserves_labelled_cargo_and_invalid_orf_is_not_certified(self):
        for broken in (False, True):
            cargo = "ATG" + ("TAA" if broken else "AAA") + "AAA" * 27 + "TAA"
            def annotate(plan):
                step = next(row for row in plan["steps"] if row["step_id"] == "cargo")
                step.update(use="seq.make_material", inputs={"sequence": {"literal": cargo}}, params={"topology": "linear", "strandedness": "double",
                    "features": [{"start": 0, "end": 90, "type": "CDS", "label": "marker", "strand": 1, "qualifiers": {"transl_table": ["1"]}}]})
            with self.subTest(broken=broken), tempfile.TemporaryDirectory() as directory:
                service, _, result = create(directory, modify_plan=annotate)
                self.assertEqual(result["state"], "COMPLETED")
                product = retained(service)["materials"]["product"][0]
                self.assertEqual(product["sequence"][50:140], cargo)
                self.assertTrue(any(row["type"] == "CDS" and row["start"] == 50 and row["end"] == 140 for row in product["features"]))
                self.assertEqual(inspect_cds(cargo, 1)["internal_stop_count"], int(broken))
                self.assertIn("check.cds_validity", service.catalog.entries)
                self.assertEqual(checked(service, "check.cds_validity")["outcome"], "FAIL" if broken else "PASS")
                self.assertEqual(checked(service, "construct.check_preparation")["outcome"], "PASS")
                self.assertEqual(checked(service, "check.model_agreement")["outcome"], "PASS")

    def test_artifact_sealing_succeeds_and_verifies(self):
        service = self.services["gibson"]
        receipt = call("seal", root=service.root)
        self.assertEqual(receipt["problems"], [], receipt)
        self.assertTrue(receipt["result"]["sealed"], receipt)
        self.assertTrue(Path(receipt["result"]["manifest"]).is_file())
        verified = call("verify", root=service.root)
        self.assertEqual(verified["problems"], [], verified)
        self.assertTrue(verified["result"]["verified"], verified)

    def test_diagnostic_judge_retains_and_satisfies_core_obligations(self):
        with tempfile.TemporaryDirectory() as directory:
            service, _, result = create(directory, "pcr", outputs="diagnostic")
            self.assertEqual(result["state"], "COMPLETED")
            receipt = call("judge", root=service.root)
            self.assertEqual(receipt["problems"], [])
            outcomes = {row["verdict"]["check"]["id"]: row["verdict"]["outcome"] for row in receipt["result"]["verdicts"]}
            # D7: valid unannotated DNA has no CDS to check; the declared
            # construction/primer obligations still have to be performed.
            expected = {"check.annotation_integrity": "PASS", "check.cds_validity": "NOT_APPLICABLE",
                        "check.biological_sanity": "PASS", "check.reaction_chain": "PASS",
                        "check.order_table": "PASS", "check.primer_quality": "PASS"}
            for identity, outcome in expected.items():
                self.assertEqual(outcomes[identity], outcome)
            self.assertEqual(receipt["result"]["unsatisfied"], [])
            self.assertEqual(outcomes["check.model_agreement"], "PASS")
            self.assertEqual(outcomes["construct.check_preparation"], "PASS")
            self.assertEqual(outcomes["construct.check_junction_assay"], "PASS")
