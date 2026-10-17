# Installation and running

Python 3.12.4 on Windows is the measured development environment. The package
declares Python >=3.11; Ubuntu and other interpreter versions are untested here.
`requirements-release.lock` records runtime dependencies, their observed installed
dependency closure and the pinned build backend. Existing core/biology locks
remain unchanged. A download installs dependencies; the toolkit itself has no
automatic installer or model-service client.

For a fresh installation from an extracted source ZIP, after authorization:

```powershell
Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-release.lock
.\.venv\Scripts\python.exe -m pip install --no-build-isolation --no-deps .
.\.venv\Scripts\python.exe -m dna_design_core.application.cli doctor
.\.venv\Scripts\python.exe -X utf8 -B examples/run_example.py --out dist/example-installed
```

The example runner clears child PYTHONPATH and PYTHONHOME. Installed-mode results
must come from the installed module, not a source-path insertion. Its independent
answer is TTCTGACT for AGTCAGAA. Output, failure logs and previous runs are retained.

For a deliberately labelled source-tree rehearsal in the existing environment:

```powershell
$env:PYTHONPATH = "src"
.\.venv\Scripts\python.exe -X utf8 -B examples/run_example.py --source-tree --out dist/example-source
```

Primer3 is optional and remains external. Without its configuration, its numerical
integration test is a registered unperformed test, never a numerical pass. The
eight-base example requires no Primer3. No fresh environment was installed as
part of S4a preparation. S4b installation results are recorded separately in
S4B-REPORT.md, not inferred from S4a. Official GitLab CI 未执行.

The wheel contains the selected source payload, four Kits and generated version
resource. Core source is copied once. The installed release manifest has the
same D16 fields as the source ZIP manifest. When a ZIP already supplies one,
the wheel builder verifies its file list and preserves its bytes. A wheel built
directly from a checkout generates its own manifest; this does not waive the
README disclosure gate or establish a successful release ZIP installation.

On run creation and verification, the installed manifest is compared with the
wheel RECORD and all its listed files are checked once per Python process.
Development-tree runs retain dev-tree. Sealed records must match the current
installed release identity when one is available. This checks file identity,
not provenance authenticity, scientific conclusions or wet-laboratory success.
Building a wheel can leave .egg-info beside source modules. That metadata does
not make a development checkout an installation: modules still running from
the project's src layout retain dev-tree. Missing manifests in actual installed
wheels remain errors.
