"""Read-only AST migration counts; old source is read, never imported or run."""
import argparse
import ast
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAPPING = {
    "sequence/operations.py": (
        ("normalize_dna", "core/tools/snapgene_io.py", "_normalise_dna"),
        ("interval_segments", "core/interval.py", "validate_interval"),
        ("slice_sequence", "core/interval.py", "extract_interval"),
        ("map_feature", "core/tools/sequence_ops.py", "_clip_feature_to_intervals"),
        ("slice_record", "core/tools/sequence_ops.py", "slice_record_interval"),
        ("rotate_record", "core/tools/sequence_ops.py", "rotate_sequence")),
    "formats/records.py": (
        ("record_projection", "core/io/molecule_codec.py", "visible_fingerprint"),
        ("read_genbank", "core/io/input_resolution.py", "_read_record_from_file"),
        ("write_genbank", "core/io/molecule_codec.py", "genbank_record"),
        ("read_fasta", "core/io/input_resolution.py", "_read_record_from_file"),
        ("write_fasta", "core/tools/snapgene_io.py", "export_snapgene"),
        ("read_dna", "core/tools/snapgene_io.py", "_read_native_data")),
    "primer/thermodynamics.py": (
        ("TmParameters", "core/tools/amplification.py", "calc_primer_tm"),
        ("calculate_tm", "core/tools/amplification.py", "calc_primer_tm")),
    "primer/quality.py": (
        ("dimer_metrics", "core/tools/amplification.py", "check_primer_dimers"),
        ("hairpin_metrics", "scripts/primer_qc.py", "score_hairpin"),
        ("primer_quality", "core/tools/amplification.py", "calc_primer_tm"),
        ("evaluate_primer_quality", "scripts/primer_qc.py", "flag_risks")),
    "primer/primer3.py": (
        ("encode_boulder", "core/tools/primer3_backend.py", "encode_boulder"),
        ("parse_boulder", "core/tools/primer3_backend.py", "parse_boulder"),
        ("primer3_check_request", "core/tools/primer3_backend.py", "check_complete_oligo_pair")),
    "pcr/prediction.py": (
        ("find_binding_sites", "core/tools/amplification.py", "_find_primer_binding"),
        ("predict_pcr_products", "core/tools/amplification.py", "simulate_pcr"),
        ("simulate_pcr", "core/tools/amplification.py", "simulate_pcr"),
        ("simulate_pcr_record", "core/tools/amplification.py", "simulate_pcr")),
    "restriction/digestion.py": (
        ("enzyme_definition", "core/tools/restriction.py", "get_enzyme"),
        ("scan_restriction_sites", "core/tools/restriction.py", "restriction_hits"),
        ("digest_sequence", "core/tools/restriction.py", "digest_sequence")),
    "assembly/simulation.py": (
        ("compatible_ends", "core/models/assembly_model.py", "compatible_sticky"),
        ("validate_duplex", "core/models/assembly_model.py", "_validate"),
        ("ligate_fragments", "core/tools/assembly.py", "ligate_fragments"),
        ("gibson_assemble", "core/models/assembly_model.py", "join_by_homology"),
        ("inverse_pcr_circularize", "core/recipes/mutagenesis.py", "recipe_site_directed_mutagenesis")),
    "materials.py": (
        ("make_material", "core/models/molecule.py", "__init__"),
        ("record_from_material", "core/models/molecule.py", "as_molecule"),
        ("material_from_record", "core/models/molecule.py", "to_dict"),
        ("material_to_duplex", "core/models/molecule.py", "__init__"),
        ("material_from_duplex", "core/models/molecule.py", "as_molecule"),
        ("material_to_genbank", "core/io/molecule_codec.py", "genbank_record"),
        ("material_from_genbank", "core/io/molecule_codec.py", "restore_file_metadata"),
        ("material_to_fasta", "core/tools/snapgene_io.py", "export_snapgene")),
    "material_operations.py": (
        ("slice_material", "core/tools/sequence_ops.py", "extract_subsequence"),
        ("rotate_material", "core/tools/sequence_ops.py", "rotate_sequence"),
        ("pcr_material", "core/tools/amplification.py", "simulate_pcr"),
        ("digest_material", "core/tools/restriction.py", "digest_sequence"),
        ("ligate_material", "core/tools/assembly.py", "ligate_fragments"),
        ("gibson_material", "core/tools/assembly.py", "simulate_overlap_assembly"),
        ("inverse_pcr_material", "core/recipes/mutagenesis.py", "recipe_site_directed_mutagenesis")),
}


def inventory(legacy: Path) -> dict:
    commit = subprocess.check_output(["git", "-C", str(legacy), "rev-parse", "HEAD"], text=True).strip()
    cache, rows = {}, []
    for module, entries in MAPPING.items():
        new_text = (ROOT / "src/dna_design_core/biology" / module).read_text(encoding="utf-8")
        new_tree = ast.parse(new_text)
        for name, old_path, old_name in entries:
            if old_path not in cache:
                text = (legacy / old_path).read_text(encoding="utf-8-sig")
                # ./ respects a legacy source folder nested inside its Git root.
                committed = subprocess.check_output(["git", "-C", str(legacy), "show", commit + ":./" + old_path]).decode("utf-8-sig")
                if text.replace("\r\n", "\n") != committed.replace("\r\n", "\n"):
                    raise AssertionError("working source differs from cited commit: " + old_path)
                tree = ast.parse(text)
                cache[old_path] = (tree, len(text.splitlines()), sorted({
                    node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
                    and node.module and (node.module.startswith("core.") or node.module in {"sg_common", "provenance", "operation_consent"})
                }))
            tree, old_file_lines, imports = cache[old_path]
            old = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == old_name)
            new = next(node for node in new_tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name == name)
            rows.append({"new_module": "biology/" + module, "new_symbol": name,
                         "old_path": "snapgene-dna-design/" + old_path, "old_symbol": old_name,
                         "old_span": [old.lineno, old.end_lineno], "old_selected_lines": old.end_lineno - old.lineno + 1,
                         "old_whole_file_lines": old_file_lines, "new_span": [new.lineno, new.end_lineno],
                         "new_selected_lines": new.end_lineno - new.lineno + 1, "new_whole_file_lines": len(new_text.splitlines()),
                         "old_project_import_modules": imports})
    return {"commit": commit, "source_files_match_cited_commit": True, "old_source_file_count": len(cache), "rows": rows}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--legacy-root", type=Path, required=True)
    arguments = parser.parse_args()
    result = inventory(arguments.legacy_root)
    folder = ROOT / "tests/evidence/s1b"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "migration-inventory.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    lines = ["| New module / symbol | Old source / symbol | Old function lines | New function/class lines |",
             "|---|---|---:|---:|"]
    for row in result["rows"]:
        lines.append(f"| `{row['new_module']}:{row['new_symbol']}` | `{row['old_path']}:{row['old_symbol']}` | {row['old_selected_lines']} | {row['new_selected_lines']} |")
    (folder / "migration-table.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"symbols": len(result["rows"]), "source_files": result["old_source_file_count"], "sources_match_commit": True}))
