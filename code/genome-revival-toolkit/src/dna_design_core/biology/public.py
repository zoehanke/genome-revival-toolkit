"""Shared pure biology and adapters to the S1 kernel material value contract."""
from .assembly.simulation import (
    compatible_ends, gibson_assemble, inverse_pcr_circularize, ligate_fragments, validate_duplex,
)
from .formats.records import (
    read_dna, read_fasta, read_genbank, record_projection, write_fasta, write_genbank,
)
from .pcr.prediction import find_binding_sites, predict_pcr_products, simulate_pcr, simulate_pcr_record
from .primer.primer3 import encode_boulder, parse_boulder, primer3_check_request
from .primer.quality import dimer_metrics, evaluate_primer_quality, hairpin_metrics, primer_quality
from .primer.thermodynamics import TmParameters, calculate_tm, calculate_tm_explicit
from .restriction.digestion import digest_sequence, enzyme_definition, scan_restriction_sites
from .sequence.operations import (
    interval_segments, map_feature, normalize_dna, reverse_complement, rotate_record, slice_record, slice_sequence,
)
from .materials import (
    make_material, material_from_duplex, material_from_genbank, material_from_record,
    material_to_duplex, material_to_fasta, material_to_genbank, record_from_material,
)
from .material_operations import (
    digest_material, gibson_material, inverse_pcr_material, ligate_material,
    pcr_material, rotate_material, slice_material,
)
from .sequence.preparation import inspect_cds, replace_material_region
from .primer.preparation import enumerate_primer_candidates, sequencing_read_coverage
from .analyzers.content import annotation_findings,cds_findings,sanity_findings

__all__ = [
    "reverse_complement",
    "TmParameters", "calculate_tm", "calculate_tm_explicit", "compatible_ends", "digest_sequence", "dimer_metrics",
    "encode_boulder", "enzyme_definition", "evaluate_primer_quality", "find_binding_sites",
    "gibson_assemble", "hairpin_metrics", "interval_segments", "inverse_pcr_circularize",
    "ligate_fragments", "map_feature", "normalize_dna", "parse_boulder", "predict_pcr_products",
    "primer3_check_request", "primer_quality", "read_dna", "read_fasta", "read_genbank",
    "record_projection", "rotate_record", "scan_restriction_sites", "simulate_pcr",
    "simulate_pcr_record", "slice_record", "slice_sequence", "validate_duplex",
    "write_fasta", "write_genbank",
    "make_material", "material_from_duplex", "material_from_genbank", "material_from_record",
    "material_to_duplex", "material_to_fasta", "material_to_genbank", "record_from_material",
    "digest_material", "gibson_material", "inverse_pcr_material", "ligate_material",
    "pcr_material", "rotate_material", "slice_material",
    "inspect_cds", "replace_material_region", "enumerate_primer_candidates", "sequencing_read_coverage",
    "annotation_findings", "cds_findings", "sanity_findings",
]
