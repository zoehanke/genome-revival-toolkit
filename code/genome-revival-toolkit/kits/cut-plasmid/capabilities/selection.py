# ported-from: genome-revival-toolkit/kits/crispr/scripts/selection.py@bf90910e5b0e67985aa37db4e0b8507cbc24f2b4
"""Conditional marker interpretation from frozen source-labelled knowledge."""
import re

from dna_design_core.kernel.public import Outcome, capability, document_id, require_schema
from dna_design_core.biology.public import inspect_cds, record_from_material
from .contracts import GENOTYPE, SELECTION, declaration, material_port, output


def marker_ids(name, rules):
    return {row["parameters"]["marker_id"] for row in rules
            if re.search(r"(?<![a-z0-9])(?:" + row["parameters"]["pattern"] + r")(?![a-z0-9])", name, re.I)}


@capability(declaration("assess_selection", "selection", "assess_selection", [material_port("vector")],
                        [output("selection", "document", "analysis", SELECTION)], {"strain_genotype": GENOTYPE}, required=[]))
def assess_selection(ctx: object, vector: dict, strain_genotype: dict | None = None) -> Outcome:
    # PROVISIONAL(S2-Q3): one frozen rule-v1 collection with individually sourced rows.
    knowledge = ctx.knowledge("kit:cut-plasmid/knowledge/selection_markers.json")
    for row in knowledge["parameters"]["rows"]:
        require_schema("rule-v1", row, "KNOWLEDGE_SOURCE_INVALID")
    rules = [row for row in knowledge["parameters"]["rows"] if row["status"] == "active"]
    genotype = strain_genotype or {}
    organism = genotype.get("organism", "").strip().casefold()
    host = ("ecoli" if organism in ("ecoli", "e. coli", "escherichia coli") else
            "yeast" if organism in ("s. cerevisiae", "saccharomyces cerevisiae") else None)
    existing = set().union(*(marker_ids(name, rules) for name in genotype.get("existing_markers", [])))
    unknown_existing = any(not marker_ids(name, rules) for name in genotype.get("existing_markers", []))
    auxotrophies = {name.strip().casefold() for name in genotype.get("auxotrophies", [])}
    markers, conflicts, unmapped = [], [], []
    record = record_from_material(vector)
    for index, feature in enumerate(record.features):
        if feature.type != "CDS":
            continue
        name = " ".join(feature.qualifiers.get("label", []) + feature.qualifiers.get("gene", []) + feature.qualifiers.get("product", []))
        keys = marker_ids(name, rules)
        if not keys:
            # A guide mislabeled CDS never becomes a selectable marker.
            if re.search("grna|sgrna|spacer|guide", name, re.I):
                conflicts.append(index)
            elif re.search("resistan|marker|antibiotic", name, re.I):
                unmapped.append(index)
            continue
        try:
            audit = inspect_cds(str(feature.extract(record.seq)), int(feature.qualifiers.get("transl_table", ["1"])[0]),
                                codon_start=int(feature.qualifiers.get("codon_start", ["1"])[0]),
                                partial=any(key in feature.qualifiers for key in ("partial", "pseudo", "pseudogene")))
        except (ValueError, KeyError, TypeError):
            conflicts.append(index)
            continue
        if audit["complete_cds_consistent"] is not True or len(keys) != 1:
            conflicts.append(index)
            continue
        key = next(iter(keys))
        alternatives = [row for row in rules if row["parameters"]["marker_id"] == key]
        compatibility, reason = "UNKNOWN", "Strain genotype was not provided."
        host_rows = [row for row in alternatives if row["parameters"]["host"] == host]
        if genotype:
            reason = "Declared host or relevant marker background is incomplete."
            if host is not None and not host_rows:
                compatibility, reason = "NOT_APPLICABLE", "Marker is mapped to another host."
            elif host_rows and "existing_markers" in genotype and not unknown_existing:
                requirement = host_rows[0]["parameters"]["auxotrophy"]
                if key in existing:
                    compatibility, reason = "CONFLICT", "Declared recipient already carries this selectable marker."
                elif requirement and "auxotrophies" not in genotype:
                    reason = "Auxotrophy was not explicitly provided."
                elif requirement and requirement not in auxotrophies:
                    compatibility, reason = "CONFLICT", "Declared recipient lacks the required auxotrophy."
                else:
                    compatibility, reason = "DECLARED_COMPATIBLE", "Conditional on declared genotype; phenotype NOT_PERFORMED."
        options = [{"host": row["parameters"]["host"], "plate": row["parameters"]["plate"],
                    "rule_id": row["id"], "rule_digest": document_id(row), "source_locator": row["source"]["locator"],
                    "compatibility": compatibility, "reason": reason} for row in host_rows] if genotype else []
        markers.append({"feature_index": index, "name": name, "marker_id": key,
                        "compatibility": compatibility, "reason": reason, "plate_options": options})
    relevant = [row for row in markers if row["compatibility"] != "NOT_APPLICABLE"]
    status = ("UNKNOWN" if not genotype else "CONFLICT" if conflicts or any(row["compatibility"] == "CONFLICT" for row in relevant) else
              "DECLARED_COMPATIBLE" if genotype and relevant and not unmapped and all(row["compatibility"] == "DECLARED_COMPATIBLE" for row in relevant) else "UNKNOWN")
    report = {"schema": "selection-assessment-v1", "claim": "selection", "status": status, "markers": markers,
              "annotation_conflicts": conflicts, "unmapped_markers": unmapped,
              "genotype_source": "user supplied; not experimentally authenticated" if genotype else "NOT_PROVIDED",
              "recipient_host": host, "message": "Strain genotype was not provided; selection is UNKNOWN." if not genotype else
              "Only explicitly declared host, existing markers and auxotrophies were used.",
              "knowledge_digest": document_id(knowledge), "draft_rows_loaded": 0}
    return Outcome(documents={"selection": report}, unverified=[
        "Selection UNKNOWN: strain genotype was not provided." if not genotype else "Recipient genotype is a declaration, not an authenticated observation.",
        "Marker expression, resistance, growth and plating: PLANNED / NOT_PERFORMED.",
        "Selection mapping sources are migrated references; source verification and team review remain unperformed."])
