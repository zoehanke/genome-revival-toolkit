# ported-from: snapgene-dna-design/core/tools/grna.py@bf90910e5b0e67985aa37db4e0b8507cbc24f2b4
# ported-from: snapgene-dna-design/core/tools/grna_evaluation.py@bf90910e5b0e67985aa37db4e0b8507cbc24f2b4
"""Directed cassette and exact supplied-sequence SpCas9 checks, no guide enumeration."""
import re

from dna_design_core.kernel.public import Outcome, ToolkitError, capability, material_id
from dna_design_core.biology.public import reverse_complement
from .contracts import CASSETTE_PARAMS, FINAL_CHECKS, GUIDE, VECTOR_SEARCH, declaration, material_port, output


def transcription_positions(boundary, length, strand, size, circular):
    positions = [boundary + index if strand == 1 else boundary - index - 1 for index in range(length)]
    if circular:
        return [index % size for index in positions]
    if any(index < 0 or index >= size for index in positions):
        raise ToolkitError("PLAN_PARAM_INVALID", "Cassette extends outside the linear sequence.")
    return positions


def parts_for(positions, strand):
    runs = []
    for position in positions:
        if runs and position == runs[-1][-1] + strand:
            runs[-1].append(position)
        else:
            runs.append([position])
    return [[min(run), max(run) + 1] for run in runs]


def cassette(vector, promoter_end, transcription_strand, scaffold_sequence):
    sequence = vector["sequence"]
    if vector["topology"] not in ("linear", "circular") or vector["strandedness"] != "double":
        raise ToolkitError("PLAN_PARAM_INVALID", "Guide inspection needs explicit topology and double-stranded DNA.")
    if not 0 <= promoter_end <= len(sequence) or len(sequence) < 20 + len(scaffold_sequence):
        raise ToolkitError("PLAN_PARAM_INVALID", "Directed cassette boundary or scaffold size is invalid.")
    positions = transcription_positions(promoter_end, 20 + len(scaffold_sequence), transcription_strand,
                                        len(sequence), vector["topology"] == "circular")
    observed = "".join(sequence[index] for index in positions)
    if transcription_strand == -1:
        observed = observed.translate(str.maketrans("ACGT", "TGCA"))
    if observed[20:] != scaffold_sequence or set(observed) - set("ACGT"):
        raise ToolkitError("PLAN_PARAM_INVALID", "Exactly 20 explicit spacer bases must precede the supplied scaffold anchor.")
    selected = positions[:20]
    return observed[:20], selected, parts_for(selected, transcription_strand)


def target_matches(material, spacer):
    sequence, size = material["sequence"], len(material["sequence"])
    if material["topology"] not in ("linear", "circular"):
        raise ToolkitError("PLAN_PARAM_INVALID", "Target topology must be explicit.")
    hits = []
    for strand in (1, -1):
        oriented = sequence if strand == 1 else reverse_complement(sequence)
        search = oriented + oriented[:22] if material["topology"] == "circular" else oriented
        for start in range(size):
            if search[start:start + 20] != spacer:
                continue
            pam = search[start + 20:start + 23]
            positions = [(start + index) % size if strand == 1 else size - 1 - ((start + index) % size)
                         for index in range(20)]
            parts = parts_for(positions, strand)
            hits.append({"strand": strand, "rna_binding_strand": -strand, "start": start,
                         "parts": parts, "pam": pam, "pam_valid": len(pam) == 3 and pam[0] in "ACGT" and pam[1:] == "GG",
                         "locus": ";".join(str(left) + ":" + str(right) for left, right in sorted(parts))})
    return hits


def annotation_findings(vector, positions, strand):
    findings = []
    for index, feature in enumerate(vector["features"]):
        parts = feature.get("parts") or [{"start": feature["start"], "end": feature["end"], "strand": feature.get("strand")}]
        overlap = any(part["start"] <= position < part["end"] for part in parts for position in positions)
        if not overlap:
            continue
        label = feature["label"] + " " + " ".join(" ".join(v) for v in feature.get("qualifiers", {}).values())
        if re.search("grna|sgrna|spacer|guide", label, re.I):
            wrong = [part.get("strand") for part in parts if part.get("strand") in (1, -1) and part["strand"] != strand]
            if wrong:
                findings.append({"code": "GRNA_ANNOTATION_STRAND_CONFLICT", "feature_index": index,
                                 "annotation_strand": wrong[0], "sequence_transcription_strand": strand})
        if feature["type"] == "CDS":
            findings.append({"code": "SPACER_ANNOTATED_AS_CDS", "feature_index": index,
                             "annotation_strand": parts[0].get("strand"), "sequence_transcription_strand": strand})
    return findings


def vector_matches(vector, spacer, max_mismatches):
    """Legacy bounded Hamming screen, supplied vector only, no bulges or other PAMs."""
    sequence, size = vector["sequence"], len(vector["sequence"])
    hits = []
    for strand in (1, -1):
        oriented = sequence if strand == 1 else reverse_complement(sequence)
        search = oriented + oriented[:22] if vector["topology"] == "circular" else oriented
        for start in range(size):
            window = search[start:start + 23]
            if len(window) != 23 or set(window) - set("ACGT") or window[21:] != "GG":
                continue
            mismatches = sum(first != second for first, second in zip(spacer, window[:20]))
            if mismatches > max_mismatches:
                continue
            positions = [(start + index) % size if strand == 1 else size - 1 - ((start + index) % size) for index in range(20)]
            parts = parts_for(positions, strand)
            hits.append({"strand": strand, "rna_binding_strand": -strand, "start": start, "parts": parts,
                         "pam": window[20:], "pam_valid": True, "mismatches": mismatches,
                         "locus": ";".join(str(left) + ":" + str(right) for left, right in sorted(parts))})
    return hits


def inspect(vector, target, promoter_end, transcription_strand, scaffold_sequence, vector_max_mismatches=3):
    spacer, positions, parts = cassette(vector, promoter_end, transcription_strand, scaffold_sequence)
    actual = target_matches(target, spacer)
    opposite = reverse_complement(spacer)
    reverse_hits = target_matches(target, opposite) if opposite != spacer else []
    valid = [hit for hit in actual if hit["pam_valid"]]
    reverse_valid = [hit for hit in reverse_hits if hit["pam_valid"]]
    direction = "CORRECT" if valid else "REVERSED" if reverse_valid else "INVALID_PAM" if actual or reverse_hits else "NO_TARGET_MATCH"
    warnings = []
    if opposite == spacer:
        warnings.append("PALINDROMIC_SPACER: sequence cannot distinguish insert orientation.")
    if len({hit["locus"] for hit in valid}) > 1:
        warnings.append("MULTIPLE_VALID_TARGETS: supplied target has multiple exact PAM-compatible loci.")
    if valid and reverse_valid:
        warnings.append("BOTH_ORIENTATIONS_HAVE_TARGETS: intended locus was not inferred.")
    return {"schema": "guide-inspection-v1", "vector_id": material_id(vector), "target_id": material_id(target),
            "promoter_end": promoter_end, "transcription_strand": transcription_strand, "spacer": spacer,
            "spacer_parts": parts, "scaffold_sequence": scaffold_sequence, "pam_valid": bool(valid),
            "direction_status": direction, "direction_correct": True if valid else False if reverse_valid else None,
            "orientation_distinguishable": opposite != spacer, "target_matches": actual,
            "reverse_insert_hypotheses": reverse_hits, "valid_target_locus_count": len({hit["locus"] for hit in valid}),
            "vector_self_targets": vector_matches(vector, spacer, vector_max_mismatches),
            "vector_max_mismatches": vector_max_mismatches, "vector_search_complete": not bool(set(vector["sequence"]) - set("ACGT")),
            "annotation_findings": annotation_findings(vector, positions, transcription_strand), "warnings": warnings}


@capability(declaration("inspect_guide", "guide", "inspect_guide", [material_port("vector"), material_port("target")],
                        [output("guide", "document", "analysis", GUIDE)], {**CASSETTE_PARAMS, **VECTOR_SEARCH},
                        required=list(CASSETTE_PARAMS), final_checks=FINAL_CHECKS))
def inspect_guide(ctx: object, vector: dict, target: dict, promoter_end: int,
                  transcription_strand: int, scaffold_sequence: str, vector_max_mismatches: int = 3) -> Outcome:
    report = inspect(vector, target, promoter_end, transcription_strand, scaffold_sequence, vector_max_mismatches)
    return Outcome(documents={"guide": report}, unverified=[
        "Supplied scaffold anchor and directed boundary are declarations; promoter and full scaffold activity NOT_PERFORMED.",
        *["Annotation finding: " + row["code"] for row in report["annotation_findings"]], *report["warnings"]])
