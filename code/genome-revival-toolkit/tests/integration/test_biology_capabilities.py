"""Run S1b through real Catalog, admitted plans, Invoker, Store and CHECK views."""
import copy
import importlib
import json
import os
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests"))
from biology_runtime import action_case, check_view, material, material_steps, retained, run_steps
from skip_registry import skip_with
from dna_design_core.biology.public import material_from_genbank
from dna_design_core.kernel import ids, schemas


class CapabilityTests(unittest.TestCase):
    def run_action(self, identity, inputs=None, parameters=None, **options):
        directory = tempfile.TemporaryDirectory(prefix="s1b_capability_")
        self.addCleanup(directory.cleanup)
        session, invoker = action_case(directory.name, identity, inputs, parameters, **options)
        return session, invoker, retained(session)

    def test_seq_make_slice_and_rotate_independent_answers(self):
        _, _, result = self.run_action(
            "seq.rotate", {"material": material("AAACCCTTTGGG", "circular", "double")}, {"origin": 2})
        self.assertEqual(result["products"]["material"][0]["sequence"], "ACCCTTTGGGAA")
        _, _, result = self.run_action("seq.slice", {"material": material("AAACCCTTTGGG", "circular", "double")}, {"start": 9, "end": 3})
        self.assertEqual(result["products"]["material"][0]["sequence"], "GGGAAA")
        # Every input above was created by a real seq.make_material step.

    def test_seq_make_material_literal_answer(self):
        with tempfile.TemporaryDirectory() as directory:
            session, _ = run_steps(directory, [{"step_id": "target", "use": "seq.make_material",
                "inputs": {"sequence": {"literal": "acgtacga"}}, "params": {}, "why": "Normalize a constructed DNA literal."}])
            self.assertEqual(retained(session)["products"]["material"][0], material("ACGTACGA"))

    def test_format_read_genbank_literal_independent_record(self):
        from unit.test_biology_sequence_formats import GENBANK
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "synthetic.gb"
            path.write_text(GENBANK, encoding="utf-8")
            session, _ = action_case(directory, "format.read_genbank", artifact_sources={"file": path})
            value = retained(session)["products"]["material"][0]
            self.assertEqual((value["sequence"], value["topology"], value["strandedness"]), ("AAACCCTTTGGG", "circular", None))
            self.assertEqual(value["features"][0]["parts"], [{"start": 9, "end": 12, "strand": 1}, {"start": 0, "end": 3, "strand": 1}])

    def test_format_read_fasta_and_native_binary(self):
        with tempfile.TemporaryDirectory() as directory:
            fasta = Path(directory) / "source.fa"
            fasta.write_text(">constructed\nAAACCCTTTGGG\n", encoding="utf-8")
            session, _ = action_case(directory, "format.read_fasta", artifact_sources={"file": fasta})
            value = retained(session)["products"]["material"][0]
            self.assertEqual(value, material("AAACCCTTTGGG"))
        with tempfile.TemporaryDirectory() as directory:
            def packet(kind, value):
                return bytes([kind]) + struct.pack(">I", len(value)) + value
            dna = Path(directory) / "source.dna"
            dna.write_bytes(packet(9, struct.pack(">8sHHH", b"SnapGene", 1, 1, 1)) + packet(0, b"\x01AAACCCTTTGGG"))
            session, _ = action_case(directory, "format.read_dna", artifact_sources={"file": dna})
            self.assertEqual(retained(session)["products"]["material"][0], material("AAACCCTTTGGG", "circular"))

    def test_format_write_genbank_then_read_independent_fields(self):
        value = material("AAACCCTTTGGG", "circular", "double", features=[{"start": 0, "end": 3, "type": "gene", "label": "synthetic", "strand": 1}])
        session, invoker, result = self.run_action("format.write_genbank", {"material": value}, {"name": "product.gb"})
        loaded = material_from_genbank(result["artifacts"][0].read_text(encoding="utf-8"))
        self.assertEqual(loaded, value)
        verdict = invoker.invoke("check.format_roundtrip", {}, {}, parent="final", view=check_view(session))
        self.assertEqual(verdict.verdicts[0]["outcome"], "PASS")
        with tempfile.TemporaryDirectory() as directory:
            fresh = Path(directory) / "source.gb"
            fresh.write_bytes(result["artifacts"][0].read_bytes())
            new, _ = action_case(directory, "format.read_genbank", artifact_sources={"file": fresh})
            self.assertEqual(retained(new)["products"]["material"][0], value)

    def test_format_write_fasta_literal_text(self):
        _, _, result = self.run_action("format.write_fasta", {"material": material("ACGTACGA")}, {"name": "product.fa"})
        self.assertEqual(result["artifacts"][0].read_text(encoding="utf-8"), ">material\nACGTACGA\n")

    def test_primer_measurements_and_binding_independent_answers(self):
        _, _, result = self.run_action("primer.calculate_tm", {"primer": material("ACGTACGA", strandedness="single")})
        self.assertEqual(result["documents"]["report"]["tm"], "11.74530033")
        _, _, result = self.run_action("primer.inspect_quality", {"primer": material("ACGTTTTTGC", strandedness="single")})
        self.assertEqual(result["documents"]["report"]["longest_T_run_nt"], 5)
        _, _, result = self.run_action("primer.find_binding_sites", {
            "template": material("AAACCCTTTGGG", "circular", "double"), "primer": material("GGAA", strandedness="single")}, {"strand": 1})
        self.assertEqual((result["documents"]["report"]["sites"][0]["start"], result["documents"]["report"]["sites"][0]["end"]), (10, 2))

    def test_pcr_actual_store_and_recorded_input_bindings(self):
        inputs = {"template": material("ACGTAACCGGTTGATC", "linear", "double"),
                  "forward": material("TTACGTA", strandedness="single"), "reverse": material("GCGATC", strandedness="single")}
        session, invoker, result = self.run_action("pcr.simulate", inputs, {"forward_core_length": 5, "reverse_core_length": 4})
        self.assertEqual(result["products"]["product"][0]["sequence"], "TTACGTAACCGGTTGATCGC")
        started = session.steps()["target"]["started"]["payload"]["inputs"]
        self.assertEqual(started["template"]["id"], ids.material_id(inputs["template"]))
        self.assertEqual(invoker.invoke("check.pcr_product", {}, {}, parent="final", view=check_view(session)).verdicts[0]["outcome"], "PASS")

    def test_restriction_scan_digest_and_ligation(self):
        _, _, result = self.run_action("restriction.scan_sites", {"material": material("CCGAATTCTT", "linear", "double")}, {"enzyme": "EcoRI"})
        hit = result["documents"]["report"]["sites"][0]
        self.assertEqual((hit["top_cut"], hit["bottom_cut"]), (3, 7))
        session, invoker, result = self.run_action("restriction.digest", {"material": material("TTGGTCTCAAGTCCCGG", "circular", "double")}, {"enzymes": ["BsaI"]})
        fragment = result["products"]["fragments"][0]
        self.assertEqual(fragment["sequence"], "AGTCCCGGTTGGTCTCA")
        self.assertEqual(invoker.invoke("check.assembly_product", {}, {}, parent="final", view=check_view(session)).verdicts[0]["outcome"], "PASS")
        _, _, closed = self.run_action("assembly.ligate", {"left": fragment}, {"circular": True})
        self.assertEqual(closed["products"]["product"][0]["sequence"], "AGTCCCGGTTGGTCTCA")
        self.assertEqual(closed["products"]["product"][0]["topology"], "circular")

    def test_gibson_and_inverse_pcr_independent_products(self):
        _, _, result = self.run_action("assembly.gibson", {
            "left": material("AAACCC", "linear", "double"), "right": material("CCCTTT", "linear", "double")}, {"overlap": 3})
        self.assertEqual(result["products"]["product"][0]["sequence"], "AAACCCTTT")
        _, _, result = self.run_action("assembly.inverse_pcr", {"template": material("AAACCCTTTGGG", "circular", "double"),
            "forward": material("ACTTT", strandedness="single"), "reverse": material("GGG", strandedness="single")}, {"forward_core_length": 3})
        self.assertEqual(result["products"]["product"][0]["sequence"], "ACTTTGGGAAACCC")
        self.assertEqual(result["products"]["intermediate"][0]["topology"], "linear")

    def test_primer3_missing_backend_returns_unknown_guidance(self):
        _, _, result = self.run_action("primer.run_primer3", {"forward": material("ACGTACGA", strandedness="single")}, config={})
        self.assertEqual(result["documents"]["report"]["outcome"], "UNKNOWN")
        self.assertIn("GRT_PRIMER3_CORE", result["documents"]["report"]["recovery"])

    @skip_with("S1B-PRIMER3-OPTIONAL", condition=lambda: not os.environ.get("GRT_PRIMER3_CORE"))
    def test_primer3_real_ctx_external_calls_and_recorded_fingerprint(self):
        configured = os.environ.get("GRT_PRIMER3_CORE", "")
        from dna_design_core.engine.invoker import Context
        real = Context.run_external
        calls = []
        def observed(ctx, argv):
            calls.append(list(argv))
            return real(ctx, argv)
        with patch.object(Context, "run_external", observed):
            _, _, result = self.run_action("primer.run_primer3", {"forward": material("ACGTACGA", strandedness="single")},
                                          config={"primer3_core": configured, "external_timeout_s": 30})
        report = result["documents"]["report"]
        if report.get("outcome") == "UNKNOWN":
            self.fail("UNKNOWN: configure GRT_PRIMER3_CORE for the actual backend integration test. " + report["reason"])
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0][1:], ["--about"])
        self.assertEqual(calls[1][1], "--strict_tags")
        self.assertEqual(report["backend"]["version"], "2.6.1")
        self.assertEqual(report["backend"]["sha256"], "19a546a0166fd979c41317e45696de1b383ab5fa21ec362bcc5053b2068b6e5f")
        self.assertEqual(report["measurements"]["PRIMER_LEFT_0_TM"], "11.745")
        folder = ROOT / "tests/evidence/s1b/integration"
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "primer3-runtime.json").write_text(json.dumps({"calls": [call[1] for call in calls],
            "backend": report["backend"], "tm": report["measurements"]["PRIMER_LEFT_0_TM"]}, indent=2) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    unittest.main()
