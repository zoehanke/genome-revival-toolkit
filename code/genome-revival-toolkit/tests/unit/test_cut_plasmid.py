"""S2 constructed answers, actual Invoker calls, independent sequence expectations."""
from copy import deepcopy
import inspect
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests"))
from cut_plasmid_runtime import KIT, b2, retained, run_case, run_check
from dna_design_core.catalog.registry import Catalog
from dna_design_core.engine.loading import Loader
from dna_design_core.engine.view import ReadView
from dna_design_core.kernel.public import document_id, require_schema


def reverse_complement(sequence):
    return sequence.translate(str.maketrans("ACGT", "TGCA"))[::-1]


def feature(start, end, label, kind="misc_RNA", strand=1):
    return {"start": start, "end": end, "type": kind, "label": label, "strand": strand}


class CutPlasmidTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)

    def run_action(self, operation="inspect_guide", case=None, parameters=None, folder="case", successful=True):
        service, result = run_case(self.directory / folder, case=case, operation=operation, parameters=parameters)
        self.assertEqual(result["state"], "COMPLETED" if successful else "HALTED", result)
        return service, retained(service) if successful else result

    def correct_case(self):
        case = b2()
        case["vector"]["sequence"] = case["expected_product"]
        return case

    def test_manifest_decorators_and_exported_contracts_match(self):
        catalog, loader = Catalog(), Loader()
        self.assertEqual(catalog.problems, [])
        manifest = json.loads((KIT / "kit.json").read_text(encoding="utf-8"))
        self.assertEqual(len(manifest["contributes"]["capabilities"]), 7)
        for name, entry in catalog.entries.items():
            if not name.startswith("cut_plasmid."):
                continue
            function = loader.load(entry)
            self.assertEqual(function.declaration, entry["declaration"])
            required_inputs = {port["name"] for port in entry["declaration"]["inputs"]}
            params = set(entry["declaration"]["params"]["properties"])
            self.assertEqual(set(inspect.signature(function).parameters) - {"ctx"}, required_inputs | params)
            require_schema("capability-v1", entry["declaration"])

    def test_all_check_pass_and_fail_fixtures_actually_run(self):
        for path in sorted((KIT / "capabilities/fixtures").glob("*.json")):
            with self.subTest(fixture=path.name):
                case = json.loads(path.read_text(encoding="utf-8"))
                service, _ = self.run_action(case=case, folder=path.stem)
                verdict = run_check(service, case["check"])
                self.assertEqual(verdict["outcome"], case["expected"], verdict)
                if case["expected"] == "FAIL":
                    self.assertNotEqual(verdict["outcome"], "PASS")

    def test_b2_wrong_pam_is_computed_from_bases(self):
        service, result = self.run_action()
        guide = result["documents"]["guide"]
        self.assertEqual(guide["spacer"], "CGACATCGTACGATCGTACA")
        self.assertFalse(guide["pam_valid"])
        self.assertEqual(guide["target_matches"][0]["pam"], "TAG")
        self.assertEqual(guide["direction_status"], "INVALID_PAM")
        self.assertEqual(run_check(service, "cut_plasmid.check_pam")["outcome"], "FAIL")

    def test_reverse_insert_is_not_rescued_by_forward_annotation(self):
        case = self.correct_case()
        sequence = case["vector"]["sequence"]
        case["vector"]["sequence"] = sequence[:130] + reverse_complement(case["spacer"]) + sequence[150:]
        case["vector"]["features"] = [feature(130, 150, "gRNA spacer", strand=1)]
        service, result = self.run_action(case=case)
        self.assertEqual(result["documents"]["guide"]["direction_status"], "REVERSED")
        self.assertEqual(run_check(service, "cut_plasmid.check_direction")["outcome"], "FAIL")

    def test_annotation_disagreement_is_reported_without_overriding_sequence(self):
        case = self.correct_case()
        case["vector"]["features"] = [feature(130, 150, "gRNA spacer", strand=-1)]
        service, result = self.run_action(case=case)
        guide = result["documents"]["guide"]
        self.assertTrue(guide["direction_correct"])
        self.assertEqual(guide["annotation_findings"][0]["code"], "GRNA_ANNOTATION_STRAND_CONFLICT")
        self.assertEqual(run_check(service, "cut_plasmid.check_direction")["outcome"], "PASS")

    def test_spacer_marked_as_cds_is_identified_and_retired(self):
        case = b2()
        case["vector"]["features"] = [feature(130, 150, "gRNA spacer", "CDS")]
        _, inspection = self.run_action(case=case, folder="inspect")
        self.assertEqual(inspection["documents"]["guide"]["annotation_findings"][0]["code"], "SPACER_ANNOTATED_AS_CDS")
        _, changed = self.run_action("replace_spacer", case=case, folder="replace")
        self.assertFalse(any(row["type"] == "CDS" for row in changed["products"]["product"]["features"]))
        self.assertEqual(changed["documents"]["route"]["annotation_changes"][0]["type"], "CDS")

    def test_b2_replacement_primers_and_linear_intermediate_match_constructed_answer(self):
        service, result = self.run_action("replace_spacer")
        case, primers = b2(), result["documents"]["primers"]
        self.assertEqual(result["products"]["product"]["sequence"], case["expected_product"])
        self.assertEqual(result["documents"]["route"]["simulation"]["linear_sequence"], case["expected_linear_product"])
        self.assertEqual([row["sequence"] for row in primers["primers"]], [case["expected_forward"], case["expected_reverse"]])
        self.assertEqual([row["core_length"] for row in primers["primers"]], [22, 27])
        self.assertEqual(primers["tm_parameters"]["dnac1_nM"], "250")
        self.assertEqual(primers["tm_parameters"]["dnac2_nM"], "0")
        self.assertAlmostEqual(float(primers["primers"][0]["tm_degC"]), 55.3176, places=4)
        self.assertAlmostEqual(float(primers["primers"][1]["tm_degC"]), 55.1042, places=4)
        self.assertTrue(all(row["performed"] == "NOT_PERFORMED" for row in result["documents"]["route"]["laboratory_steps"]))
        self.assertTrue(any("homopolymer" in note for note in primers["quality_notes"]))
        nested = [event for event in service.session.events() if event["type"] == "call.recorded"]
        self.assertTrue(any(row["payload"]["capability"]["id"] == "assembly.inverse_pcr" for row in nested))
        self.assertTrue(all(row["payload"]["parent"] == "test" for row in nested))
        for name in ("check_direction", "check_pam", "check_vector_self_target"):
            self.assertEqual(run_check(service, "cut_plasmid." + name)["outcome"], "PASS")

    def test_independent_model_matches_constructed_edit(self):
        _, result = self.run_action("model_replace")
        self.assertEqual(result["products"]["product"]["sequence"], b2()["expected_product"])

    def test_wrapping_origin_replacement_and_negative_transcription(self):
        original = b2()
        for negative in (False, True):
            case = deepcopy(original)
            # Independent coordinate transformation: original cassette starts at 350.
            origin = 140
            case["vector"]["sequence"] = original["vector"]["sequence"][origin:] + original["vector"]["sequence"][:origin]
            expected = original["expected_product"][origin:] + original["expected_product"][:origin]
            case["params"]["promoter_end"] = 350
            if negative:
                case["vector"]["sequence"] = reverse_complement(case["vector"]["sequence"])
                case["params"].update(promoter_end=10, transcription_strand=-1)
                expected = reverse_complement(expected)
            _, result = self.run_action("replace_spacer", case=case, folder=str(negative))
            self.assertEqual(result["products"]["product"]["sequence"], expected)
            self.assertEqual(len(result["documents"]["route"]["spacer_parts"]), 2)

    def test_tm_window_rejects_impossible_design_with_positive_control(self):
        self.run_action("replace_spacer", folder="positive")
        parameters = {**b2()["params"], "spacer": b2()["spacer"], "tm_min": "100", "tm_max": "101"}
        _, failed = self.run_action("replace_spacer", parameters=parameters, folder="negative", successful=False)
        self.assertEqual(failed["failure"]["code"], "PLAN_PARAM_INVALID")

    def test_second_binding_site_blocks_design_with_positive_control(self):
        self.run_action("replace_spacer", folder="positive")
        case = b2()
        sequence = case["vector"]["sequence"]
        # Copy all candidate F binding cores, not merely the selected 22-mer.
        case["vector"]["sequence"] = sequence[:240] + sequence[150:186] + sequence[276:]
        _, failed = self.run_action("replace_spacer", case=case, folder="negative", successful=False)
        self.assertGreater(failed["failure"]["details"]["ambiguous_binding_count"], 0)

    def test_missing_genotype_is_unknown_and_has_no_plate_recommendation(self):
        for bad_annotation in (False, True):
            case = b2()
            if bad_annotation:
                case["vector"]["features"] = [feature(130, 150, "gRNA spacer", "CDS")]
            _, result = self.run_action("assess_selection", case=case, folder=str(bad_annotation))
            selection = result["documents"]["selection"]
            self.assertEqual(selection["status"], "UNKNOWN")
            self.assertEqual(selection["genotype_source"], "NOT_PROVIDED")
            if bad_annotation:
                self.assertEqual(selection["annotation_conflicts"], [0])

    def test_source_labelled_mapping_requires_complete_declared_genotype(self):
        case = b2()
        # Synthetic complete CDS, deliberately no resistance/function claim.
        case["vector"]["sequence"] = "ATGAAATAA" + case["vector"]["sequence"][9:]
        case["vector"]["features"] = [feature(0, 9, "LEU2", "CDS")]
        for name, parameters, expected in (
            ("missing", {}, "UNKNOWN"),
            ("declared", {"strain_genotype": {"organism": "S. cerevisiae", "existing_markers": [], "auxotrophies": ["leu2"]}}, "DECLARED_COMPATIBLE"),
            ("conflict", {"strain_genotype": {"organism": "S. cerevisiae", "existing_markers": ["LEU2"], "auxotrophies": ["leu2"]}}, "CONFLICT"),
            ("incomplete", {"strain_genotype": {"organism": "S. cerevisiae", "existing_markers": []}}, "UNKNOWN")):
            _, result = self.run_action("assess_selection", case=case, parameters=parameters, folder=name)
            report = result["documents"]["selection"]
            self.assertEqual(report["status"], expected)
            if name == "declared":
                option = report["markers"][0]["plate_options"][0]
                self.assertEqual(option["plate"], "Synthetic defined medium without leucine")
                self.assertIn("yeastgenome.org", option["source_locator"])
            if name == "missing":
                self.assertEqual(report["markers"][0]["plate_options"], [])

    def test_all_migrated_host_rows_keep_sources_and_no_fabricated_receipts(self):
        pack = json.loads((KIT / "knowledge/selection_markers.json").read_text(encoding="utf-8"))
        rows = [row for row in pack["parameters"]["rows"] if "legacy_rule_id" in row["parameters"]]
        self.assertEqual(len(rows), 10)
        self.assertEqual({row["parameters"]["marker_id"] for row in rows}, {"amp", "kan", "cat", "hph", "nat", "ura3", "his3", "leu2", "trp1"})
        for row in rows:
            require_schema("rule-v1", row)
            self.assertEqual(row["source"]["verification_status"], "unverified")
            self.assertNotIn("verification_receipt", row["source"])
            self.assertTrue(row["source"]["citation"] and row["source"]["locator"])

    def test_vector_near_match_and_ambiguous_bases_do_not_become_pass(self):
        for name in ("near", "ambiguous"):
            case = self.correct_case()
            sequence = case["vector"]["sequence"]
            if name == "near":
                mutated = ("C" if case["spacer"][0] != "C" else "A") + case["spacer"][1:]
                case["vector"]["sequence"] = sequence[:20] + mutated + "TGG" + sequence[43:]
            else:
                case["vector"]["sequence"] = "N" + sequence[1:]
            service, result = self.run_action(case=case, folder=name)
            self.assertEqual(run_check(service, "cut_plasmid.check_vector_self_target")["outcome"], "UNKNOWN")
            if name == "near":
                self.assertTrue(any(row["mismatches"] == 1 for row in result["documents"]["guide"]["vector_self_targets"]))

    def test_multiple_target_loci_are_counted_without_choosing_one(self):
        case = self.correct_case()
        case["target"]["sequence"] += "AAAAA" + case["spacer"] + "TGG"
        _, result = self.run_action(case=case)
        guide = result["documents"]["guide"]
        self.assertEqual(guide["valid_target_locus_count"], 2)
        self.assertTrue(any("MULTIPLE_VALID_TARGETS" in item for item in guide["warnings"]))

    def test_model_agreement_detects_a_constructed_one_base_wrong_product(self):
        service, result = self.run_action("replace_spacer")
        self.assertEqual(run_check(service, "check.model_agreement")["outcome"], "PASS")
        wrong = deepcopy(result["products"]["product"])
        wrong["sequence"] = ("A" if wrong["sequence"][0] != "A" else "C") + wrong["sequence"][1:]
        identity = service.session.store.put("materials", wrong)
        # A deliberately inconsistent in-memory check fixture, never a history rewrite.
        events = service.session.events()
        for event in events:
            if event["type"] == "step.completed" and event["payload"]["step_id"] == "test":
                event["payload"]["outputs"]["materials"]["product"] = [identity]
        view = ReadView(service.root, events, service.session.snapshot(), {"moment": "final", "issuer": "check_capability", "catalog": service.session.snapshot()})
        verdict = service.invoker.invoke("check.model_agreement", {}, {}, parent="judge", view=view).verdicts[0]
        self.assertEqual(verdict["outcome"], "FAIL")
        self.assertEqual(service.session.events()[-1]["type"], "run.completed")

    def test_untouched_invalid_cds_retains_sequence_and_annotation(self):
        case = b2()
        case["vector"]["features"] = [feature(10, 18, "preexisting invalid CDS", "CDS")]
        service, result = self.run_action("replace_spacer", case=case)
        source_id = service.session.steps()["read_vector"]["completed"]["payload"]["outputs"]["materials"]["material"][0]
        original = service.session.store.get("materials", source_id)
        retained_cds = [row for row in result["products"]["product"]["features"] if row["type"] == "CDS"]
        self.assertEqual(retained_cds, original["features"])
        # This test establishes retention only. D7 inherited PASS/introduced FAIL is blocked by S2-Q1.


if __name__ == "__main__":
    unittest.main()
