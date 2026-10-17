# Reproducible build and separate installation verification

Use the provisioned environment. The commands below set PYTHONPATH=src for the
development commands. Product and Kit sources are selected by ship.json, not a
second hand-maintained copy. Internal evidence, private machine paths, caches,
development-only inventories and binaries do not belong in the source ZIP.

```powershell
$env:PYTHONPATH = "src"
.\.venv\Scripts\python.exe -X utf8 -B tools/build_release.py --third-party-only
.\.venv\Scripts\python.exe -X utf8 -B tools/check_release.py --report dist/release-check.json
.\.venv\Scripts\python.exe -X utf8 -B tools/build_release.py --out dist/release-a
.\.venv\Scripts\python.exe -X utf8 -B tools/build_release.py --out dist/release-b
```

Generate THIRD_PARTY.md, finish the real pending documentation, then freeze and
commit those source inputs before building a candidate. Dependency metadata is
used only by the explicit generation command; assembly reads the frozen file.
The default build identifier is the source commit. Both builds must use that
same source tree and identifier. ZIP entries are sorted, use a fixed 1980 UTC
timestamp and fixed file modes, and store bytes without platform-dependent
compression. The manifest uses canonical JSON and contains no self hash or own
file entry. Its SHA-256 is release_id; the archive has a separate SHA-256 sidecar.
VERSIONS.json is the only version source. Its installed-resource copy and
THIRD_PARTY.md are generated. Dependency binaries are not copied. The wheel
build command uses the same ship.json selection and retains each source path
in the manifest. Core modules install directly under dna_design_core; other
selected files install below that package with their source-relative paths.
Thus the installed runtime can check the full manifest without a second Core
copy. Wheel RECORD anchors the manifest bytes.

An unfinished disclosure or architecture marker gives INCOMPLETE and a nonzero
exit, with no ZIP. Resolve each real pending item before producing a candidate.
Synthetic text used by automated tests belongs only to test copies.

After a valid source ZIP exists, prepare the fresh-environment command without
running installation:

```powershell
$env:PYTHONPATH = "src"
.\.venv\Scripts\python.exe -X utf8 -B tools/check_release.py --zip dist/release-a/ARCHIVE.zip
.\.venv\Scripts\python.exe -X utf8 -B tools/clean_env_verify.py --archive dist/release-a/ARCHIVE.zip --workdir dist/clean-verification --report dist/clean-plan.json
```

Replace ARCHIVE.zip with the emitted filename. The plan creates no environment
and installs nothing. Ask the user for the separate authorization required by
S4a task item 4. Only after that authorization, run the same command with
`--execute`. It creates a venv without system site packages, installs the exact
release lock and local project, clears child PYTHONPATH, checks the installed
module location, runs the synthetic example and verifies every bundled sealed
example. The new run's release identity must match the archive manifest; a
development-tree identity remains INCOMPLETE. Commands, outputs and failures
stay in the new work directory, including output written before an interruption.

An installed release refuses a seal from a different release_id. In particular,
the retained dev-tree example is not a release-identity match: it is inspectable
in a source checkout, and cannot serve as a matching installed-release example.
S4b leaves the ZIP execution path unverified while three human disclosure items
remain; a future release needs matching release examples before that path can
pass. No missing disclosure is filled by the build command.

The original workspace is not an installation test. A passing engineering build
does not declare S4 complete, freeze a new candidate, upload code or supply human
review. Official GitLab CI 未执行. GitHub CI has not been run for S4a.
