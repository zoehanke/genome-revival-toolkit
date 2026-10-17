"""Primer3 subprocess adapter. Every launch goes through ctx.run_external(argv)."""
from pathlib import Path
import re
import subprocess

from dna_design_core.kernel.public import Outcome, capability, file_sha256
from dna_design_core.biology.public import TmParameters, parse_boulder, primer3_check_request
from .._biology import concentration_properties, declaration, input_errors, output, port

MODULE = __name__


@capability(declaration("primer.run_primer3", "Run local Primer3 on complete supplied oligos, recording executable version and hashes.", MODULE, "run_primer3",
    [port("forward"), port("reverse", required=False)],
    [output("report", "document", "analysis"), output("request", "artifact", None), output("response", "artifact", None)],
    concentration_properties(), effects=("reads_files", "writes_files", "external_process")))
@input_errors
def run_primer3(ctx: object, forward: dict, reverse: dict | None = None, sodium_mM: str = "50",
                magnesium_mM: str = "0", dntp_mM: str = "0", total_oligo_nM: str = "50") -> Outcome:
    parameters = TmParameters(sodium_mM, magnesium_mM, dntp_mM, total_oligo_nM)
    parameters.concentrations()
    configured = ctx.config.get("primer3_core")
    executable = Path(configured).resolve() if configured else None
    thermodynamic = executable.parent / "primer3_config" if executable else Path("primer3_config")
    request = primer3_check_request(forward["sequence"], reverse=None if reverse is None else reverse["sequence"],
                                    parameters=parameters, thermodynamic_path=str(thermodynamic) + "/")
    request_path, response_path = ctx.workdir / "primer3-input.txt", ctx.workdir / "primer3-output.txt"
    request_path.write_text(request, encoding="utf-8", newline="\n")
    response_path.write_text("", encoding="utf-8", newline="\n")
    recovery = "Set GRT_PRIMER3_CORE through application configuration to a local primer3_core executable with its primer3_config directory. No automatic installation."

    def unknown(reason, backend=None):
        return Outcome(documents={"report": {"outcome": "UNKNOWN", "reason": reason, "recovery": recovery,
            "backend": backend, "parameters": {"sodium_mM": sodium_mM, "magnesium_mM": magnesium_mM,
                "dntp_mM": dntp_mM, "total_oligo_nM": total_oligo_nM}}},
            artifacts={"request": request_path, "response": response_path}, unverified=[reason + " " + recovery])

    if executable is None or not executable.is_file() or not thermodynamic.is_dir():
        return unknown("Primer3 executable or thermodynamic data are unavailable.")
    checksum = file_sha256(executable.read_bytes())
    backend = {"name": "primer3_core", "sha256": checksum}
    try:
        about = ctx.run_external([str(executable), "--about"])
        match = re.search(r"release\s+(\d+\.\d+\.\d+)", about.stdout + about.stderr)
        if match is None:
            return unknown("Primer3 version could not be identified.", backend)
        backend["version"] = match.group(1)
        backend["thermodynamic_files"] = {path.name: file_sha256(path.read_bytes()) for path in sorted(thermodynamic.iterdir()) if path.is_file()}
        completed = ctx.run_external([str(executable), "--strict_tags", str(request_path)])
        response_path.write_text(completed.stdout, encoding="utf-8", newline="\n")
        if file_sha256(executable.read_bytes()) != checksum:
            return unknown("Primer3 executable changed during execution.", backend)
        raw = parse_boulder(completed.stdout)
        if raw.get("PRIMER_ERROR") or "PRIMER_LEFT_0_TM" not in raw:
            return unknown("Primer3 returned no complete oligo measurements.", backend)
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired, ValueError) as error:
        return unknown("Primer3 could not complete the configured request: " + type(error).__name__, backend)
    return Outcome(documents={"report": {"backend": backend, "parameters": {
        "sodium_mM": sodium_mM, "magnesium_mM": magnesium_mM, "dntp_mM": dntp_mM,
        "total_oligo_nM": total_oligo_nM, "tm_formula": 1, "salt_corrections": 1},
        "measurements": raw}}, artifacts={"request": request_path, "response": response_path},
        unverified=["Primer3 measurements do not establish PCR specificity or wet-laboratory success."])
